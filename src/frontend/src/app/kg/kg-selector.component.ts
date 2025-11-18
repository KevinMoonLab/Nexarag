import { Component, inject, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DropdownModule } from 'primeng/dropdown';
import { ButtonModule } from 'primeng/button';
import { ToastModule } from 'primeng/toast';
import { FormsModule } from '@angular/forms';
import { MessageService } from 'primeng/api';
import { KnowledgeGraphService, KnowledgeGraphInfo } from './kg.service';
import { GraphStore } from '../graph/graph.store';

@Component({
  selector: 'app-kg-selector',
  standalone: true,
  imports: [CommonModule, DropdownModule, ButtonModule, ToastModule, FormsModule],
  providers: [MessageService],
  template: `
    <div class="flex items-center gap-2">
      <span class="text-sm text-white font-medium">Knowledge Graph:</span>
      <p-dropdown 
        [options]="knowledgeGraphs()" 
        [(ngModel)]="selectedKg"
        optionLabel="name" 
        optionValue="name"
        placeholder="Select Knowledge Graph"
        [loading]="loading()"
        styleClass="w-48"
        (onChange)="onSelectionChange()">
        <ng-template pTemplate="selectedItem" let-option>
          <div *ngIf="option">{{ option }}</div>
        </ng-template>
        <ng-template pTemplate="item" let-option>
          <div class="flex flex-col">
            <span class="font-medium">{{ option.name }}</span>
            <span class="text-sm text-gray-600">{{ option.size_mb | number:'1.1-1' }} MB</span>
          </div>
        </ng-template>
      </p-dropdown>
      <p-button 
        icon="pi pi-refresh" 
        severity="secondary"
        size="small"
        [loading]="loading()"
        (click)="refresh()"
        pTooltip="Refresh list">
      </p-button>
    </div>
    <p-toast></p-toast>
  `,
  styles: [`
    :host {
      display: inline-block;
    }
  `]
})
export class KgSelectorComponent implements OnInit {
  private kgService = inject(KnowledgeGraphService);
  private messageService = inject(MessageService);
  private graphStore = inject(GraphStore);

  knowledgeGraphs = signal<KnowledgeGraphInfo[]>([]);
  loading = signal(false);
  selectedKg: string | null = null;

  ngOnInit() {
    this.loadKnowledgeGraphs();
  }

  loadKnowledgeGraphs() {
    this.loading.set(true);
    this.kgService.listKnowledgeGraphs().subscribe({
      next: (kgs) => {
        this.knowledgeGraphs.set(kgs);
        this.loading.set(false);
      },
      error: (error) => {
        console.error('Error loading knowledge graphs:', error);
        this.loading.set(false);
      }
    });
  }

  onSelectionChange() {
    if (this.selectedKg) {
      this.loading.set(true);
      this.kgService.importKnowledgeGraph(this.selectedKg).subscribe({
        next: (response) => {
          if (response.success) {
            this.messageService.add({
              severity: 'success',
              summary: 'Success',
              detail: `Switched to knowledge graph: ${this.selectedKg}`
            });
            this.graphStore.refreshGraph(); // Refresh the graph visualization
          } else {
            this.messageService.add({
              severity: 'error',
              summary: 'Error',
              detail: response.message
            });
          }
          this.loading.set(false);
        },
        error: (error) => {
          console.error('Error switching knowledge graph:', error);
          this.messageService.add({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to switch knowledge graph'
          });
          this.loading.set(false);
        }
      });
    }
  }

  refresh() {
    this.loadKnowledgeGraphs();
  }
}
