import { Component, inject, model, OnInit, ViewEncapsulation } from '@angular/core';
import { CommonModule } from '@angular/common';
import { InputTextModule } from 'primeng/inputtext';
import { FormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { ChatService } from './chat.service';

@Component({
  selector: 'app-chat',
  imports: [CommonModule, InputTextModule, FormsModule, ButtonModule],
  template: `
    <div class="flex flex-row items-center space-x-2">
        <input id="query" placeholder="Enter query" pInputText [(ngModel)]="query"   />
        <p-button label="Search" (onClick)="submitQuery()" />
    </div>
  `,
  styles: [],
  encapsulation: ViewEncapsulation.None,
})
export class ChatComponent implements OnInit {
  query = model('');
  chatService = inject(ChatService);

  ngOnInit(): void {
    this.chatService.startConnection();
    this.chatService.addReceiveEchoListener(this.handleReceive);
  }

  submitQuery(): void {
    this.chatService.sendEcho(this.query());
  }

  handleReceive(message: string): void {
    console.log(message);
  }
}
