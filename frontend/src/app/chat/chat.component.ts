import { Component, computed, effect, ElementRef, inject, model, OnInit, signal, ViewChild, ViewEncapsulation } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { ChatService } from './chat.service';
import { DividerModule } from 'primeng/divider';
import { TabsModule } from 'primeng/tabs';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { marked } from 'marked';

@Component({
  selector: 'app-chat',
  imports: [CommonModule, ButtonModule, DividerModule, ButtonModule, FormsModule, TabsModule],
  template: `
    <p-tabs value="0" class="h-full">
      <p-tablist>
          <p-tab value="0">Chat</p-tab>
          <p-tab value="1">Research Assistant</p-tab>
      </p-tablist>
      <p-tabpanels class="h-full">
          <p-tabpanel class="h-full" value="0">
            <div class="flex flex-col h-full">
              <!-- Chat message area -->
              <div #scrollContainer class="flex-1 overflow-y-auto space-y-4 p-6">
                <ng-container *ngFor="let message of chat.messages()">
                  <div [ngClass]="{'justify-start': !message.isUser, 'justify-end': message.isUser}" class="flex items-start gap-2">
                    <span *ngIf="!message.isUser" class="pi pi-sparkles text-2xl bg-gray-100 rounded-full p-2"></span>
                    <div class="p-3 rounded-lg shadow-md bg-white prose prose-sm"
                      [innerHTML]="renderMarkdown(message.text)">
                    </div>
                    <span *ngIf="message.isUser" class="pi pi-user text-2xl bg-gray-100 rounded-full p-2"></span>
                  </div>
                </ng-container>

                <div *ngIf="chat.isThinking()" class="flex items-start gap-2 justify-start">
                  <span class="pi pi-sparkles text-2xl bg-gray-100 rounded-full p-2"></span>
                  <div class="min-w-[3em] max-w-[80%] p-3 rounded-lg shadow-md bg-gray-100">
                    {{ chat.typingMessage() }}
                  </div>
                </div>
              </div>

              <!-- Input area -->
              <div class="p-4 flex items-center gap-2">
                <textarea
                  pInputTextarea
                  class="flex-1 text-black resize-none p-2 border rounded-lg"
                  rows="2"
                  placeholder="Type a message..."
                  [(ngModel)]="chat.message"
                ></textarea>
                <button pButton [disabled]="!chat.message().length || !chat.responseComplete()" icon="pi pi-arrow-circle-up" class="p-button-primary" (click)="handleNewMessage()"> </button>
              </div>
            </div>
          </p-tabpanel>

          <p-tabpanel class="h-full" value="1">
            <div class="flex flex-col h-full">
            <!-- Chat message area -->
            <div #scrollContainer class="flex-1 overflow-y-auto space-y-4 p-6">
              <ng-container *ngFor="let message of chat.messages()">
                <div [ngClass]="{'justify-start': !message.isUser, 'justify-end': message.isUser}" class="flex items-start gap-2">
                  <span *ngIf="!message.isUser" class="pi pi-sparkles text-2xl bg-gray-100 rounded-full p-2"></span>
                  <div class="max-w-[80%] p-3 rounded-lg shadow-md bg-white prose prose-sm"
                      [innerHTML]="renderMarkdown(message.text)">
                  </div>
                  <span *ngIf="message.isUser" class="pi pi-user text-2xl bg-gray-100 rounded-full p-2"></span>
                </div>
              </ng-container>

              <div *ngIf="chat.isThinking()" class="flex items-start gap-2 justify-start">
                <span class="pi pi-sparkles text-2xl bg-gray-100 rounded-full p-2"></span>
                <div class="min-w-[3em] max-w-[80%] p-3 rounded-lg shadow-md bg-gray-100">
                  {{ chat.typingMessage() }}
                </div>
              </div>
            </div>


              <!-- Input area -->
              <div class="p-4 flex items-center gap-2">
                <textarea
                  pInputTextarea
                  class="flex-1 text-black resize-none p-2 border rounded-lg"
                  rows="2"
                  placeholder="Type a message..."
                  [(ngModel)]="chat.message"
                ></textarea>
                <button pButton [disabled]="!chat.message().length || !chat.responseComplete()" icon="pi pi-arrow-circle-up" class="p-button-primary" (click)="handleNewMessage()"> </button>
              </div>
            </div>
          </p-tabpanel>
      </p-tabpanels>
  </p-tabs>
  `,
  styles: [],
  encapsulation: ViewEncapsulation.None,
})
export class ChatComponent {

  @ViewChild('scrollContainer') scrollContainer!: ElementRef;
  chat = inject(ChatService);

  constructor(private sanitizer: DomSanitizer) {}

  private message = `<p>To leverage the structure of a latent space in diffusion models for influencing generation, several approaches can be employed:</p>

<ol>
  <li>
    <strong>Vector Arithmetic</strong>: Utilize vector operations within the latent space to perform semantic image manipulations, allowing for controlled edits by traversing along specific directions.
  </li>
  <li>
    <strong>Hierarchical Semantic Features</strong>: Employ encoders to capture structured representations at different levels of abstraction, enhancing conditional generation capabilities and enabling more intricate pattern capturing.
  </li>
  <li>
    <strong>Guidance Techniques</strong>: Adjust latent variables during the generation process through guidance methods, which can steer the output towards desired attributes or styles.
  </li>
  <li>
    <strong>Intermediate Bottlenecks as Semantic Spaces</strong>: Identify and use bottleneck layers in the model architecture as a semantic space (e.g., "h-space") for effective image editing by manipulating these intermediate representations.
  </li>
</ol>

<p>These techniques collectively enhance the controllability and quality of generated outputs in diffusion models.</p>
`

  renderMarkdown(text: string): SafeHtml {
    const html = marked.parse(text) as string;
    return this.sanitizer.bypassSecurityTrustHtml(this.message);
  }

  thinkingEffect = effect(() => {
    const thinking = this.chat.isThinking();
    if (thinking) this.scrollToBottom();
  });

  newMessageEffect = effect(() => {
    const messages = this.chat.messages();
    if (messages.length) this.scrollToBottom();
  })

  handleNewMessage() {
    this.chat.sendMessage();
  }

  private scrollToBottom() {
    if (this.scrollContainer?.nativeElement) {
      this.scrollContainer.nativeElement.scrollTop = this.scrollContainer.nativeElement.scrollHeight;
    }
  }
}
