import { TestBed, fakeAsync, tick } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { ChatService } from './chat.service';
import { EventService, Event } from '../events.service';
import { ChatMessage, ChatResponse } from './types';
import { Subject } from 'rxjs';

describe('ChatService', () => {
  let service: ChatService;
  let httpMock: HttpTestingController;
  let eventsSubject: Subject<Event>;

  beforeEach(() => {
    eventsSubject = new Subject<Event>();

    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [
        ChatService,
        {
          provide: EventService,
          useValue: { events$: eventsSubject.asObservable() },
        },
      ],
    });

    service = TestBed.inject(ChatService);
    httpMock = TestBed.inject(HttpTestingController);

    // Flush constructor requests: default prefix + model list
    const prefixReq = httpMock.expectOne((r) => r.url.includes('/chat/prefix/default/'));
    prefixReq.flush('You are a helpful assistant.');

    const modelsReq = httpMock.expectOne((r) => r.url.includes('/ollama/list/'));
    modelsReq.flush({
      models: [
        { model: 'llama3', size: 8000000000 },
        { model: 'nomic-embed-text', size: 500000000 },
        { model: 'mistral', size: 7000000000 },
      ],
    });
  });

  afterEach(() => {
    httpMock.verify();
    service.stopTyping(); // Clean up any intervals
  });

  // --- Initial state ---

  describe('initial state', () => {
    it('should load default prompt from backend', () => {
      expect(service.prompt()).toBe('You are a helpful assistant.');
    });

    it('should filter out nomic models', () => {
      expect(service.models().length).toBe(2);
      expect(service.models().every((m) => !m.model.includes('nomic'))).toBe(true);
    });

    it('should start with empty messages', () => {
      expect(service.userMessages()).toEqual([]);
      expect(service.responseMessageList()).toEqual([]);
      expect(service.messages()).toEqual([]);
    });

    it('should start with responseComplete as true', () => {
      expect(service.responseComplete()).toBe(true);
    });
  });

  // --- groupBy ---

  describe('groupBy', () => {
    it('should group items by key', () => {
      const items = [
        { category: 'a', value: 1 },
        { category: 'b', value: 2 },
        { category: 'a', value: 3 },
      ];
      const result = service.groupBy(items, (i) => i.category);
      expect(result['a']).toHaveLength(2);
      expect(result['b']).toHaveLength(1);
    });

    it('should return empty object for empty array', () => {
      const result = service.groupBy([], (i: any) => i.key);
      expect(result).toEqual({});
    });
  });

  // --- responseMessages computed ---

  describe('responseMessages', () => {
    it('should concatenate messages with the same responseId', () => {
      const chunks: ChatResponse[] = [
        { responseId: 'r1', userMessageId: 'u1', message: 'Hello ', chatId: 'c1' },
        { responseId: 'r1', userMessageId: 'u1', message: 'world', chatId: 'c1' },
      ];
      service.responseMessageList.set(chunks);

      const result = service.responseMessages();
      expect(result).toHaveLength(1);
      expect(result[0].message).toBe('Hello world');
      expect(result[0].responseId).toBe('r1');
    });

    it('should keep separate responses separate', () => {
      const chunks: ChatResponse[] = [
        { responseId: 'r1', userMessageId: 'u1', message: 'First', chatId: 'c1' },
        { responseId: 'r2', userMessageId: 'u2', message: 'Second', chatId: 'c1' },
      ];
      service.responseMessageList.set(chunks);

      const result = service.responseMessages();
      expect(result).toHaveLength(2);
    });
  });

  // --- messages computed (pairing user messages with responses) ---

  describe('messages computed', () => {
    it('should pair user messages with their responses', () => {
      service.userMessages.set([
        { message: 'Hi', chatId: 'c1', messageId: 'u1', model: 'llama3', prefix: '' },
      ]);
      service.responseMessageList.set([
        { responseId: 'r1', userMessageId: 'u1', message: 'Hello!', chatId: 'c1' },
      ]);

      const msgs = service.messages();
      expect(msgs).toHaveLength(2);
      expect(msgs[0]).toEqual({ text: 'Hi', isUser: true, messageId: 'u1' });
      expect(msgs[1]).toEqual({ text: 'Hello!', isUser: false, messageId: 'r1' });
    });

    it('should show user message without response when response is empty', () => {
      service.userMessages.set([
        { message: 'Hi', chatId: 'c1', messageId: 'u1', model: 'llama3', prefix: '' },
      ]);

      const msgs = service.messages();
      // Only the user message (empty response filtered out)
      expect(msgs).toHaveLength(1);
      expect(msgs[0].isUser).toBe(true);
    });

    it('should handle multiple conversation turns', () => {
      service.userMessages.set([
        { message: 'Q1', chatId: 'c1', messageId: 'u1', model: 'llama3', prefix: '' },
        { message: 'Q2', chatId: 'c1', messageId: 'u2', model: 'llama3', prefix: '' },
      ]);
      service.responseMessageList.set([
        { responseId: 'r1', userMessageId: 'u1', message: 'A1', chatId: 'c1' },
        { responseId: 'r2', userMessageId: 'u2', message: 'A2', chatId: 'c1' },
      ]);

      const msgs = service.messages();
      expect(msgs).toHaveLength(4);
      expect(msgs.map((m) => m.text)).toEqual(['Q1', 'A1', 'Q2', 'A2']);
    });
  });

  // --- messageObject computed ---

  describe('messageObject', () => {
    it('should omit chatId when chatId is empty (new conversation)', () => {
      service.message.set('Hello');
      service.prompt.set('Be helpful');
      service.selectedModel.set('llama3');
      service.chatId.set('');

      const obj = service.messageObject();
      expect(obj.message).toBe('Hello');
      expect(obj.model).toBe('llama3');
      expect(obj.prefix).toBe('Be helpful');
      expect(obj.chatId).toBeUndefined();
    });

    it('should include chatId when one is set', () => {
      service.chatId.set('chat-123');
      service.message.set('Follow-up');

      const obj = service.messageObject();
      expect(obj.chatId).toBe('chat-123');
    });

    it('should fall back to first model when no model is explicitly selected', () => {
      service.selectedModel.set('');
      service.message.set('test');

      const obj = service.messageObject();
      expect(obj.model).toBe('llama3');
    });
  });

  // --- send (HTTP) ---

  describe('send', () => {
    it('should POST to /chat/send/ with the message payload', () => {
      const msg: ChatMessage = {
        message: 'Hello',
        chatId: 'c1',
        messageId: 'u1',
        model: 'llama3',
        prefix: '',
      };

      service.send(msg).subscribe();

      const req = httpMock.expectOne((r) => r.url.includes('/chat/send/'));
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(msg);
      req.flush({ chatId: 'c1', messageId: 'u1' });
    });
  });

  // --- WebSocket event handlers ---

  describe('handleChatResponse (via WebSocket)', () => {
    it('should append response chunks to responseMessageList', () => {
      const chunk: ChatResponse = {
        responseId: 'r1',
        userMessageId: 'u1',
        message: 'Hello',
        chatId: 'c1',
      };

      eventsSubject.next({ type: 'chat_response', body: chunk });

      expect(service.responseMessageList()).toHaveLength(1);
      expect(service.responseMessageList()[0]).toEqual(chunk);
    });

    it('should ignore empty messages', () => {
      const empty: ChatResponse = {
        responseId: 'r1',
        userMessageId: 'u1',
        message: '',
        chatId: 'c1',
      };

      eventsSubject.next({ type: 'chat_response', body: empty });
      expect(service.responseMessageList()).toHaveLength(0);
    });

    it('should stop typing indicator on first response chunk', () => {
      service.startThinking();
      expect(service.isThinking()).toBe(true);

      eventsSubject.next({
        type: 'chat_response',
        body: { responseId: 'r1', userMessageId: 'u1', message: 'Hi', chatId: 'c1' },
      });

      expect(service.isThinking()).toBe(false);
    });
  });

  describe('handleResponseCompleted (via WebSocket)', () => {
    it('should set responseComplete to true', () => {
      service.responseComplete.set(false);

      eventsSubject.next({ type: 'response_completed', body: {} });

      expect(service.responseComplete()).toBe(true);
    });
  });

  // --- startNewConversation ---

  describe('startNewConversation', () => {
    it('should reset all conversation state', () => {
      service.chatId.set('c1');
      service.userMessages.set([
        { message: 'Hi', chatId: 'c1', messageId: 'u1', model: 'llama3', prefix: '' },
      ]);
      service.responseMessageList.set([
        { responseId: 'r1', userMessageId: 'u1', message: 'Hello', chatId: 'c1' },
      ]);
      service.message.set('draft');
      service.prompt.set('custom prompt');

      service.startNewConversation();

      expect(service.chatId()).toBe('');
      expect(service.userMessages()).toEqual([]);
      expect(service.responseMessageList()).toEqual([]);
      expect(service.message()).toBe('');
      expect(service.prompt()).toBe('');
    });
  });

  // --- Thinking indicator ---

  describe('thinking indicator', () => {
    afterEach(() => {
      service.stopTyping();
    });

    it('startThinking should set isThinking to true', () => {
      service.startThinking();
      expect(service.isThinking()).toBe(true);
    });

    it('stopTyping should set isThinking to false', () => {
      service.startThinking();
      service.stopTyping();
      expect(service.isThinking()).toBe(false);
    });

    it('startThinking should not restart if already thinking', () => {
      service.startThinking();
      const first = service.isThinking();
      service.startThinking(); // should not reset
      expect(service.isThinking()).toBe(first);
    });
  });

  // --- getDefaultPrefix ---

  describe('getDefaultPrefix', () => {
    it('should fetch the default prompt prefix', () => {
      service.getDefaultPrefix().subscribe((prefix) => {
        expect(prefix).toBe('System prompt');
      });

      const req = httpMock.expectOne((r) => r.url.includes('/chat/prefix/default/'));
      req.flush('System prompt');
    });
  });

  // --- updateModels ---

  describe('updateModels', () => {
    it('should refresh the models list from backend', () => {
      service.updateModels();

      const req = httpMock.expectOne((r) => r.url.includes('/ollama/list/'));
      req.flush({
        models: [{ model: 'phi3', size: 3000000000 }],
      });

      expect(service.allModels()).toHaveLength(1);
      expect(service.allModels()[0].model).toBe('phi3');
    });
  });
});
