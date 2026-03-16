import { EventService, Event } from './events.service';

// Mock WebSocket
class MockWebSocket {
  onopen: ((ev: any) => void) | null = null;
  onmessage: ((ev: any) => void) | null = null;
  onclose: ((ev: any) => void) | null = null;
  onerror: ((ev: any) => void) | null = null;

  simulateOpen() {
    this.onopen?.({});
  }

  simulateMessage(data: any) {
    this.onmessage?.({ data: JSON.stringify(data) });
  }

  simulateClose() {
    this.onclose?.({});
  }

  simulateError(error: any) {
    this.onerror?.(error);
  }
}

describe('EventService', () => {
  let service: EventService;
  let mockWs: MockWebSocket;
  const originalWebSocket = globalThis.WebSocket;

  beforeEach(() => {
    jest.useFakeTimers();
    mockWs = new MockWebSocket();
    (globalThis as any).WebSocket = jest.fn(() => mockWs);
    service = new EventService();
  });

  afterEach(() => {
    globalThis.WebSocket = originalWebSocket;
    jest.useRealTimers();
  });

  it('should connect to the WebSocket URL on construction', () => {
    expect(globalThis.WebSocket).toHaveBeenCalledWith(
      expect.stringContaining('ws://')
    );
  });

  it('should set connectionStatus to true on open', (done) => {
    service.connectionStatus$.subscribe((status) => {
      if (status) {
        expect(status).toBe(true);
        done();
      }
    });
    mockWs.simulateOpen();
  });

  it('should parse and emit events from WebSocket messages', (done) => {
    const testEvent: Event = { type: 'graph_updated', body: { foo: 'bar' } };

    service.events$.subscribe((event) => {
      expect(event).toEqual(testEvent);
      done();
    });

    mockWs.simulateMessage(testEvent);
  });

  it('should emit different event types correctly', () => {
    const received: Event[] = [];
    service.events$.subscribe((event) => received.push(event));

    const events: Event[] = [
      { type: 'graph_updated', body: {} },
      { type: 'chat_response', body: { message: 'hello' } },
      { type: 'response_completed', body: {} },
      { type: 'plot_created', body: { data: [] } },
    ];

    events.forEach((e) => mockWs.simulateMessage(e));

    expect(received).toEqual(events);
  });

  it('should set connectionStatus to false on close', (done) => {
    mockWs.simulateOpen();

    let openSeen = false;
    service.connectionStatus$.subscribe((status) => {
      if (status) {
        openSeen = true;
      } else if (openSeen) {
        expect(status).toBe(false);
        done();
      }
    });

    mockWs.simulateClose();
  });

  it('should attempt to reconnect after 3 seconds on close', () => {
    const constructorSpy = globalThis.WebSocket as unknown as jest.Mock;
    expect(constructorSpy).toHaveBeenCalledTimes(1);

    // Capture the new mock that will be created on reconnect
    const reconnectMock = new MockWebSocket();
    constructorSpy.mockReturnValueOnce(reconnectMock);

    mockWs.simulateClose();

    // Before 3 seconds — no reconnect yet
    jest.advanceTimersByTime(2999);
    expect(constructorSpy).toHaveBeenCalledTimes(1);

    // At 3 seconds — reconnect
    jest.advanceTimersByTime(1);
    expect(constructorSpy).toHaveBeenCalledTimes(2);
  });

  it('should handle errors without crashing', () => {
    expect(() => {
      mockWs.simulateError(new Error('connection failed'));
    }).not.toThrow();
  });
});
