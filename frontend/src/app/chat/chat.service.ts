import { HttpClient } from "@angular/common/http";
import { computed, inject, Injectable, signal } from "@angular/core";
import { map, Observable, Subject, switchMap } from "rxjs";
import { environment } from "src/environments/environment";
import { Event, EventService } from "../events.service";
import { ChatMessage, ChatResponse, ModelDetails } from "./types";

@Injectable({
    providedIn: 'root',
  })
  export class ChatService {
    #http = inject(HttpClient);
    #events = inject(EventService);

    // Chat context
    chatId = signal('');
    responseComplete = signal(true);
    userMessages = signal([] as ChatMessage[]);
    responseMessageList = signal([] as ChatResponse[]);
    responseMessages = computed(() => {
      const grouped = this.groupBy(this.responseMessageList(), (msg) => msg.responseId);
      const results = Object.values(grouped).map(g => ({ ...g[0], message: g.map(m => m.message).join('') }));
      return results;
    });

    messages = computed(() => {
      const userMessages = this.userMessages();
      const responseMessages = this.responseMessages();
      const mapped = new Map<string, ChatResponse>();
      responseMessages.forEach(msg => mapped.set(msg.userMessageId, msg));
      const paired = userMessages.map(msg => ({ userMessage: msg, responseMessage: mapped.get(msg.messageId) }));
      const result = paired.map(pair => ([
        { text: pair.userMessage.message, isUser: true, messageId: pair.userMessage.messageId },
        { text: pair.responseMessage?.message || '', isUser: false, messageId: pair.responseMessage?.responseId || '' }
      ])).flat().filter(f => f.text.length > 0);
      return result;
    });

    message = signal('');
    prompt = signal('');
    messageObject = computed(() => {
      if (this.chatId() === '') {
        return { 
          message: this.message(), 
          model: this.getSelectedModel(),
          prefix: this.prompt()
        } as ChatMessage;
      }

      return { 
        message: this.message(), 
        chatId: this.chatId(), 
        model: this.getSelectedModel(),
        prefix: this.prompt()
      } as ChatMessage;
    });

    // Thinking indicator
    isThinking = signal(false);
    private typingInterval: any;
    typingMessage = signal('');

    // New message subject
    #messageSubject = new Subject<ChatMessage>();

    // Models
    allModels = signal([] as ModelDetails[]);
    models = computed(() => this.allModels().filter(m => !m.model.includes('nomic')));
    #updateModelsSubject = new Subject<void>();
    selectedModel = signal('');
  
    constructor() {
      this.#events.events$.subscribe((event) => {
        if (event.type === 'chat_response') {
          this.handleChatResponse(event.body);
        } else if (event.type === 'response_completed') {
          this.handleResponseCompleted(event.body);
        }
      });

      this.#messageSubject.pipe(
        switchMap(this.send.bind(this))        )
        .subscribe(this.messageAdded.bind(this));

      this.#updateModelsSubject.pipe(
        switchMap(this.getModels.bind(this))
      ).subscribe((models) => {
        this.allModels.set(models);
      });

      this.getDefaultPrefix()
        .subscribe(p => this.prompt.set(p));

      this.#updateModelsSubject.next();
    }

    private handleChatResponse(data: ChatResponse) {
      this.stopTyping();
      this.responseMessageList.update(prev => [...prev, data]);
    }

    private handleResponseCompleted(data: any) {
      this.responseComplete.set(true);
    }
  
    public send(message: ChatMessage): Observable<any> {
      const url = environment.apiBaseUrl + '/chat/send/';
      return this.#http.post(url, message);
    }

    public startNewConversation() {
      this.chatId.set('');
      this.userMessages.set([]);
      this.responseMessageList.set([]);
      this.message.set('');
      this.prompt.set('');
    }

    public getDefaultPrefix(): Observable<string> {
      const url = environment.apiBaseUrl + '/chat/prefix/default/';
      return this.#http.get<string>(url);
    }

    private getModels(): Observable<ModelDetails[]> {
      const url = environment.apiBaseUrl + '/ollama/list/';
      return this.#http.get<any>(url).pipe(map(res => res.models));
    }

    private getSelectedModel() {
      return this.selectedModel() || this.models()[0]?.model;
    }

    public updateModels() {
      this.#updateModelsSubject.next();
    }

    private messageAdded(newMessage: ChatMessage) {
      // Update msg state
      this.userMessages.update(prev => [...prev, newMessage]);
      this.message.set('');
      this.chatId.set(newMessage.chatId);
      this.responseComplete.set(false);

      // Start thinking
      this.startThinking();
    }

    public sendMessage() {
      console.log('Sending message:', this.messageObject());
      this.#messageSubject.next(this.messageObject());
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

    groupBy<T, K extends keyof any>(array: T[], keyGetter: (item: T) => K): Record<K, T[]> {
      return array.reduce((result, item) => {
          const key = keyGetter(item);
          if (!result[key]) {
              result[key] = [];
          }
          result[key].push(item);
          return result;
      }, {} as Record<K, T[]>);
    }
  }