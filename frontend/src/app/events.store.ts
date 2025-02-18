import { Injectable, inject } from "@angular/core";
import { Subject, Observable, BehaviorSubject } from "rxjs";
import { environment } from "src/environments/environment";

@Injectable({
    providedIn: "root",
})
export class EventStore {
    private socket!: WebSocket;
    private eventSubject = new Subject<any>();
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
            console.log("Received message:", event);
            const data = JSON.parse(event.data);
            console.log("Received WebSocket event:", data);
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

    get events$(): Observable<any> {
        return this.eventSubject.asObservable();
    }

    get connectionStatus$(): Observable<boolean> {
        return this.connectionStatus.asObservable();
    }
}
