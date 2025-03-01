import { Component, computed, effect, ElementRef, inject, model, OnInit, signal, ViewChild, ViewEncapsulation } from '@angular/core';
import { CommonModule } from '@angular/common';
import { InputTextModule } from 'primeng/inputtext';
import { FormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { ChatService } from './chat.service';
import { DividerModule } from 'primeng/divider';

@Component({
  selector: 'app-chat',
  imports: [CommonModule, ButtonModule, DividerModule, ButtonModule, FormsModule],
  template: `
    <div class="flex flex-col h-full">
      <!-- Scrollable chat area -->
      <div #scrollContainer class="flex-1 overflow-y-auto space-y-4 p-6">
        <ng-container *ngFor="let message of chat.messages()">
          <div [ngClass]="{'justify-start': !message.isUser, 'justify-end': message.isUser}" class="flex items-start gap-2">
            <!-- Chat head (user or other person) -->
            <span *ngIf="!message.isUser" class="pi pi-sparkles text-2xl bg-gray-700 rounded-full p-2"></span>
            <div class="max-w-[80%] p-3 rounded-lg shadow-md"
                 [ngClass]="{'bg-blue-500 text-white': message.isUser, 'bg-gray-700 text-white': !message.isUser}">
              {{ message.text }}
            </div>
            <span *ngIf="message.isUser" class="pi pi-user text-2xl bg-gray-700 rounded-full p-2"></span>
          </div>
        </ng-container>

        <div *ngIf="chat.isThinking()" class="flex items-start gap-2 justify-start">
          <span class="pi pi-sparkles text-2xl bg-gray-700 rounded-full p-2"></span>
          <div class="min-w-[3em] max-w-[80%] p-3 rounded-lg shadow-md bg-gray-700 text-white">
            {{ chat.typingMessage() }}
          </div>
        </div>
      </div>

      <!-- Fixed input area -->
      <div class="p-4 flex items-center gap-2">
        <textarea
          pInputTextarea
          class="flex-1 text-black resize-none p-2 border rounded-lg"
          rows="2"
          placeholder="Type a message..."
          [(ngModel)]="chat.message"
        ></textarea>
        <button pButton [disabled]="!chat.message().length" icon="pi pi-arrow-circle-up" class="p-button-primary" (click)="handleNewMessage()"> </button>
      </div>
    </div>
  `,
  styles: [],
  encapsulation: ViewEncapsulation.None,
})
export class ChatComponent {

  @ViewChild('scrollContainer') scrollContainer!: ElementRef;
  chat = inject(ChatService);

  thinkingEffect = effect(() => {
    const thinking = this.chat.isThinking();
    if (thinking) this.scrollToBottom();
  });

  handleNewMessage() {
    this.chat.sendMessage();
    setTimeout(() => this.scrollToBottom(), 200);
  }

  private scrollToBottom() {
    if (this.scrollContainer?.nativeElement) {
      this.scrollContainer.nativeElement.scrollTop = this.scrollContainer.nativeElement.scrollHeight;
    }
  }
}
