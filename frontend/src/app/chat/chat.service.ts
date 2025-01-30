import { Injectable } from "@angular/core";
import * as signalR from '@microsoft/signalr';

@Injectable({
    providedIn: 'root',
  })
  export class ChatService {
    private hubConnection: signalR.HubConnection;
  
    constructor() {
      this.hubConnection = new signalR.HubConnectionBuilder()
        .withUrl('http://localhost:8080/live/chat')
        .build();
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
  
    public sendEcho(message: string): Promise<void> {
      return this.hubConnection.invoke('Echo', message);
    }
  }