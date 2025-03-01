import { HttpClient } from "@angular/common/http";
import { inject, Injectable, signal } from "@angular/core";
import * as signalR from '@microsoft/signalr';
import { Observable, Subject, switchMap } from "rxjs";
import { environment } from "src/environments/environment";

@Injectable({
    providedIn: 'root',
  })
  export class ChatService {
    private hubConnection: signalR.HubConnection;
    #http = inject(HttpClient);

    // Chat context
    chatId = signal('');
    messages = signal([] as { text: string; isUser: boolean }[]);
    message = signal('');

    // Thinking indicator
    isThinking = signal(false);
    private typingInterval: any;
    typingMessage = signal('');

    // New message subject
    #messageSubject = new Subject<string>();
  
    constructor() {
      this.hubConnection = new signalR.HubConnectionBuilder()
        .withUrl('http://localhost:8080/ws/chat')
        .build();

      this.#messageSubject.pipe(
        switchMap(this.send.bind(this))        )
        .subscribe(this.messageAdded.bind(this));
    }
  
    public startConnection(): Promise<void> {
      return this.hubConnection
        .start()
        .then(() => console.log('Connection started'))
        .catch((err) => console.error('Error while starting connection: ' + err));
    }
  
    public addReceiveEchoListener(callback: (message: string) => void): void {
      this.hubConnection.on('ReceiveEcho', callback);
    }
  
    public send(message: string): Observable<any> {
      const url = environment.apiBaseUrl + '/chat/send/';
      const chatId = this.chatId();
      return this.#http.post(url, { message, chatId });
    }

    private messageAdded(result: any) {
      console.log('Message added:', result);
      // Update msg state
      const newMessage = this.message();
      this.messages.update(prev => [...prev, { text: newMessage, isUser: true }]);
      this.message.set('');

      // Start thinking
      this.startThinking();
    }

    public sendMessage() {
      this.#messageSubject.next(this.message());
    }

    startThinking() {
      if (!this.isThinking()) {
        this.isThinking.set(true);
        const dots = ['.', '..', '...'];
        let index = 0;
        this.typingInterval = setInterval(() => {
          this.typingMessage.set(dots[index]);
          index = (index + 1) % dots.length;
        }, 500);
      }
    }
  
    stopTyping() {
      this.isThinking.set(false);
      clearInterval(this.typingInterval);
    }
  }