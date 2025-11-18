import { Component, inject, signal, computed, OnInit } from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { InputTextModule } from 'primeng/inputtext';
import { TextareaModule } from 'primeng/textarea';
import { DropdownModule } from 'primeng/dropdown';
import { ConfirmDialogModule } from 'primeng/confirmdialog';
import { ToastModule } from 'primeng/toast';
import { DialogModule } from 'primeng/dialog';
import { FormsModule } from '@angular/forms';
import { ConfirmationService, MessageService } from 'primeng/api';
import { KnowledgeGraphService, KnowledgeGraphInfo, CurrentKgInfo } from './kg.service';

@Component({
  selector: 'app-kg-management',
  standalone: true,
  imports: [
    CommonModule,
    ButtonModule,
    CardModule,
    InputTextModule,
    TextareaModule,
    DropdownModule,
    ConfirmDialogModule,
    ToastModule,
    DialogModule,
    FormsModule,
    DatePipe
  ],
  providers: [ConfirmationService, MessageService],
  template: `
    <div class="p-6 h-full overflow-auto">
      <div class="mb-6">
        <h2 class="text-2xl font-bold text-white mb-4">Knowledge Graph Management</h2>
        
        <!-- Current KG Info -->
        <p-card class="mb-6">
          <ng-template pTemplate="header">
            <div class="text-lg font-semibold">Current Knowledge Graph</div>
          </ng-template>
          <div class="flex items-center justify-between">
            <div>
              <p><strong>Database:</strong> {{ currentKgInfo()?.database }}</p>
              <p><strong>Status:</strong> {{ currentKgInfo()?.status }}</p>
            </div>
            <p-button 
              label="Refresh" 
              icon="pi pi-refresh" 
              (click)="loadCurrentKgInfo()"
              [loading]="loadingCurrent()">
            </p-button>
          </div>
        </p-card>

        <!-- Export Section -->
        <p-card class="mb-6">
          <ng-template pTemplate="header">
            <div class="text-lg font-semibold">Export Current Knowledge Graph</div>
          </ng-template>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium mb-2">Name</label>
              <input 
                pInputText 
                [(ngModel)]="exportName" 
                placeholder="Enter export name"
                class="w-full">
            </div>
            <div class="md:col-span-2">
              <label class="block text-sm font-medium mb-2">Description (Optional)</label>
              <textarea 
                pInputTextarea 
                [(ngModel)]="exportDescription" 
                placeholder="Enter description"
                class="w-full"
                rows="3">
              </textarea>
            </div>
            <div class="md:col-span-2">
              <p-button 
                label="Export Knowledge Graph" 
                icon="pi pi-download" 
                (click)="exportKg()"
                [loading]="loadingExport()"
                [disabled]="!exportName.trim()">
              </p-button>
            </div>
          </div>
        </p-card>
      </div>

      <!-- Knowledge Graphs List -->
      <p-card>
        <ng-template pTemplate="header">
          <div class="flex items-center justify-between">
            <div class="text-lg font-semibold">Available Knowledge Graphs</div>
            <p-button 
              label="Refresh" 
              icon="pi pi-refresh" 
              (click)="loadKnowledgeGraphs()"
              [loading]="loadingList()">
            </p-button>
          </div>
        </ng-template>
        
        <div *ngIf="knowledgeGraphs().length === 0" class="text-center py-8 text-gray-500">
          No knowledge graphs found. Export your current graph to get started.
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4" *ngIf="knowledgeGraphs().length > 0">
          <div *ngFor="let kg of knowledgeGraphs()" class="border rounded-lg p-4 bg-gray-50">
            <div class="mb-3">
              <h3 class="font-semibold text-lg">{{ kg.name }}</h3>
              <p class="text-sm text-gray-600" *ngIf="kg.description">{{ kg.description }}</p>
            </div>
            
            <div class="text-sm text-gray-500 mb-4">
              <p><strong>Created:</strong> {{ kg.created_at | date:'medium' }}</p>
              <p><strong>Size:</strong> {{ kg.size_mb | number:'1.1-1' }} MB</p>
            </div>
            
            <div class="flex gap-2">
              <p-button 
                label="Load" 
                icon="pi pi-upload" 
                size="small"
                severity="success"
                (click)="loadKg(kg.name)"
                [loading]="loadingOperation() === kg.name">
              </p-button>
              <p-button 
                label="Delete" 
                icon="pi pi-trash" 
                size="small"
                severity="danger"
                (click)="confirmDelete(kg.name)"
                [loading]="loadingOperation() === kg.name">
              </p-button>
            </div>
          </div>
        </div>
      </p-card>
    </div>

    <p-confirmDialog></p-confirmDialog>
    <p-toast></p-toast>
  `,
  styles: [`
    :host {
      display: block;
      height: 100%;
    }
  `]
})
export class KgManagementComponent implements OnInit {
  private kgService = inject(KnowledgeGraphService);
  private confirmationService = inject(ConfirmationService);
  private messageService = inject(MessageService);

  knowledgeGraphs = signal<KnowledgeGraphInfo[]>([]);
  currentKgInfo = signal<CurrentKgInfo | null>(null);
  loadingList = signal(false);
  loadingCurrent = signal(false);
  loadingExport = signal(false);
  loadingOperation = signal<string | null>(null);

  exportName = '';
  exportDescription = '';

  ngOnInit() {
    this.loadKnowledgeGraphs();
    this.loadCurrentKgInfo();
  }

  loadKnowledgeGraphs() {
    this.loadingList.set(true);
    this.kgService.listKnowledgeGraphs().subscribe({
      next: (kgs) => {
        this.knowledgeGraphs.set(kgs);
        this.loadingList.set(false);
      },
      error: (error) => {
        console.error('Error loading knowledge graphs:', error);
        this.messageService.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to load knowledge graphs'
        });
        this.loadingList.set(false);
      }
    });
  }

  loadCurrentKgInfo() {
    this.loadingCurrent.set(true);
    this.kgService.getCurrentKgInfo().subscribe({
      next: (info) => {
        this.currentKgInfo.set(info);
        this.loadingCurrent.set(false);
      },
      error: (error) => {
        console.error('Error loading current KG info:', error);
        this.messageService.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to load current knowledge graph info'
        });
        this.loadingCurrent.set(false);
      }
    });
  }

  exportKg() {
    if (!this.exportName.trim()) return;

    this.loadingExport.set(true);
    this.kgService.exportKnowledgeGraph(this.exportName.trim(), this.exportDescription.trim() || undefined)
      .subscribe({
        next: (response) => {
          if (response.success) {
            this.messageService.add({
              severity: 'success',
              summary: 'Success',
              detail: response.message
            });
            this.exportName = '';
            this.exportDescription = '';
            this.loadKnowledgeGraphs(); // Refresh the list
          } else {
            this.messageService.add({
              severity: 'error',
              summary: 'Error',
              detail: response.message
            });
          }
          this.loadingExport.set(false);
        },
        error: (error) => {
          console.error('Error exporting knowledge graph:', error);
          this.messageService.add({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to export knowledge graph'
          });
          this.loadingExport.set(false);
        }
      });
  }

  loadKg(name: string) {
    this.loadingOperation.set(name);
    this.kgService.importKnowledgeGraph(name).subscribe({
      next: (response) => {
        if (response.success) {
          this.messageService.add({
            severity: 'success',
            summary: 'Success',
            detail: response.message
          });
          this.loadCurrentKgInfo(); // Refresh current info
        } else {
          this.messageService.add({
            severity: 'error',
            summary: 'Error',
            detail: response.message
          });
        }
        this.loadingOperation.set(null);
      },
      error: (error) => {
        console.error('Error loading knowledge graph:', error);
        this.messageService.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to load knowledge graph'
        });
        this.loadingOperation.set(null);
      }
    });
  }

  confirmDelete(name: string) {
    this.confirmationService.confirm({
      message: `Are you sure you want to delete the knowledge graph "${name}"? This action cannot be undone.`,
      header: 'Confirm Delete',
      icon: 'pi pi-exclamation-triangle',
      acceptButtonStyleClass: 'p-button-danger',
      accept: () => {
        this.deleteKg(name);
      }
    });
  }

  deleteKg(name: string) {
    this.loadingOperation.set(name);
    this.kgService.deleteKnowledgeGraph(name).subscribe({
      next: (response) => {
        if (response.success) {
          this.messageService.add({
            severity: 'success',
            summary: 'Success',
            detail: response.message
          });
          this.loadKnowledgeGraphs(); // Refresh the list
        } else {
          this.messageService.add({
            severity: 'error',
            summary: 'Error',
            detail: response.message
          });
        }
        this.loadingOperation.set(null);
      },
      error: (error) => {
        console.error('Error deleting knowledge graph:', error);
        this.messageService.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to delete knowledge graph'
        });
        this.loadingOperation.set(null);
      }
    });
  }
}
