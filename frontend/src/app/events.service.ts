import { Injectable, inject } from "@angular/core";
import { Subject, Observable, BehaviorSubject } from "rxjs";
import { environment } from "src/environments/environment";

export type Event = {
    type: 'graph_updated' | 'chat_response' | 'response_completed' | 'plot_created';
    body: any;
}

@Injectable({
    providedIn: "root",
})
export class EventService {
    private socket!: WebSocket;
    private eventSubject = new Subject<Event>();
    private connectionStatus = new BehaviorSubject<boolean>(false);

    constructor() {
        this.connect();
    }

    private connect(): void {
        this.socket = new WebSocket(environment.webSocketUrl);

        this.socket.onopen = () => {
            console.log("Connected to WebSocket");
            this.connectionStatus.next(true);
        };

        this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.eventSubject.next(data);
        };

        this.socket.onclose = () => {
            console.warn("WebSocket connection closed. Attempting to reconnect...");
            this.connectionStatus.next(false);
            setTimeout(() => this.connect(), 3000);
        };

        this.socket.onerror = (error) => {
            console.error("WebSocket error:", error);
        };
    }

    get events$(): Observable<Event> {
        return this.eventSubject.asObservable();
    }

    get connectionStatus$(): Observable<boolean> {
        return this.connectionStatus.asObservable();
    }
}
