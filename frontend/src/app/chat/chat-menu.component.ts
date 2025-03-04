import { Component, computed, inject, model, OnInit, signal, ViewEncapsulation } from '@angular/core';
import { CommonModule } from '@angular/common';
import { InputTextModule } from 'primeng/inputtext';
import { FormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { ChatService } from './chat.service';
import { DividerModule } from 'primeng/divider';
import { ChatComponent } from "./chat.component";

@Component({
  selector: 'app-chat-menu',
  imports: [CommonModule, ButtonModule, DividerModule, ChatComponent],
  template: `
    <div class="h-screen bg-gray-800 text-white flex transition-all duration-300" [ngClass]="{'w-[40rem]': expanded(), 'w-16': !expanded()}">
      
      <div class="w-16 flex flex-col items-center border-r border-gray-700 p-2">
        <p-button icon="{{ icon() }}" class="p-button-rounded p-button-text text-white mt-4" (click)="toggleMenu()"></p-button>
        <p-button *ngFor="let tab of tabs; let i = index" 
                  icon="{{ tab.icon }}" 
                  class="p-button-rounded p-button-text text-white mt-6" 
                  (click)="selectTab(i)">
        </p-button>
      </div>

      <div *ngIf="expanded()" class="flex-grow">
        <ng-container *ngIf="selectedTab() === 0">
          <app-chat />
        </ng-container>
        <ng-container *ngIf="selectedTab() === 1">
          <p class="text-lg">Chat History</p>
          <p-divider />
        </ng-container>
      </div>

    </div>
  `,
  styles: [],
  encapsulation: ViewEncapsulation.None,
})
export class ChatMenuComponent {
    expanded = signal(false);
    selectedTab = signal(0);
  
    icon = computed(() => this.expanded() ? 'pi pi-angle-right' : 'pi pi-angle-left');
    tabs = [
      { icon: 'pi pi-plus', label: 'New Conversation' },
      { icon: 'pi pi-history', label: 'History' }
    ];
  
    toggleMenu() {
      this.expanded.update(prev => !prev);
    }
  
    selectTab(index: number) {
      this.selectedTab.set(index);
      this.expanded.set(true);
    }
}
