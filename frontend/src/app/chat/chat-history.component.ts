import { Component, computed, inject, model, OnInit, signal, ViewEncapsulation } from '@angular/core';
import { CommonModule } from '@angular/common';
import { InputTextModule } from 'primeng/inputtext';
import { FormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { ChatService } from './chat.service';
import { DividerModule } from 'primeng/divider';

@Component({
  selector: 'app-chat-history',
  imports: [CommonModule, ButtonModule, DividerModule],
  template: `
    <div class="flex flex-col space-y-4">
      Chat history
    </div>  
  `,
  styles: [],
  encapsulation: ViewEncapsulation.None,
})
export class ChatHistoryComponent {
}
