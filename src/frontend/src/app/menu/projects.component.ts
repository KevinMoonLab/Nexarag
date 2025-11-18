import { Component, computed, effect, inject, signal, OnInit } from '@angular/core';
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
import { KnowledgeGraphService, KnowledgeGraphInfo, CurrentKgInfo } from '../kg/kg.service';
import { GraphStore } from '../graph/graph.store';


@Component({
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
    selector: 'app-projects',
    template: `
        <div class="p-4 h-full overflow-auto">
            <h3 class="text-xl font-bold text-white mb-4">Knowledge Graph Projects</h3>
            
            <!-- Current KG Info -->
            <div class="mb-6 p-4 bg-gray-800 rounded-lg">
                <h4 class="text-lg font-semibold text-white mb-3">Current Project</h4>
                <div class="flex items-center justify-between">
                    <div class="text-gray-300">
                        <p><strong>Database:</strong> {{ currentKgInfo()?.database || 'neo4j' }}</p>
                        <p><strong>Status:</strong> {{ currentKgInfo()?.status || 'active' }}</p>
                    </div>
                    <p-button 
                        label="Refresh" 
                        icon="pi pi-refresh" 
                        size="small"
                        severity="secondary"
                        (click)="loadCurrentKgInfo()"
                        [loading]="loadingCurrent()">
                    </p-button>
                </div>
            </div>

            <!-- Export Section -->
            <div class="mb-6 p-4 bg-gray-800 rounded-lg">
                <h4 class="text-lg font-semibold text-white mb-3">Export Current Project</h4>
                <div class="grid grid-cols-1 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-300 mb-2">Project Name</label>
                        <input 
                            pInputText 
                            [(ngModel)]="exportName" 
                            placeholder="Enter project name"
                            class="w-full">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-300 mb-2">Description (Optional)</label>
                        <textarea 
                            pInputTextarea 
                            [(ngModel)]="exportDescription" 
                            placeholder="Enter description"
                            class="w-full"
                            rows="3">
                        </textarea>
                    </div>
                    <div>
                        <p-button 
                            label="Export Project" 
                            icon="pi pi-download" 
                            (click)="exportKg()"
                            [loading]="loadingExport()"
                            [disabled]="!exportName.trim()">
                        </p-button>
                    </div>
                </div>
            </div>

            <!-- Projects List -->
            <div class="p-4 bg-gray-800 rounded-lg">
                <div class="flex items-center justify-between mb-4">
                    <h4 class="text-lg font-semibold text-white">Saved Projects</h4>
                    <p-button 
                        label="Refresh" 
                        icon="pi pi-refresh" 
                        size="small"
                        severity="secondary"
                        (click)="loadKnowledgeGraphs()"
                        [loading]="loadingList()">
                    </p-button>
                </div>
                
                <div *ngIf="knowledgeGraphs().length === 0" class="text-center py-8 text-gray-400">
                    No saved projects found. Export your current project to get started.
                </div>

                <div class="grid grid-cols-1 gap-4" *ngIf="knowledgeGraphs().length > 0">
                    <div *ngFor="let kg of knowledgeGraphs()" class="border border-gray-600 rounded-lg p-4 bg-gray-700">
                        <div class="mb-3">
                            <h5 class="font-semibold text-lg text-white">{{ kg.name }}</h5>
                            <p class="text-sm text-gray-300" *ngIf="kg.description">{{ kg.description }}</p>
                        </div>
                        
                        <div class="text-sm text-gray-400 mb-4">
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
            </div>
        </div>

        <p-confirmDialog></p-confirmDialog>
        <p-toast></p-toast>
    `
})
export class ProjectsComponent implements OnInit {
    private kgService = inject(KnowledgeGraphService);
    private confirmationService = inject(ConfirmationService);
    private messageService = inject(MessageService);
    state = inject(GraphStore);

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
                    detail: 'Failed to load projects'
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
                    detail: 'Failed to load current project info'
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
                        detail: 'Failed to export project'
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
                    this.state.refreshGraph(); // Refresh the graph visualization
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
                    detail: 'Failed to load project'
                });
                this.loadingOperation.set(null);
            }
        });
    }

    confirmDelete(name: string) {
        this.confirmationService.confirm({
            message: `Are you sure you want to delete the project "${name}"? This action cannot be undone.`,
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
                    detail: 'Failed to delete project'
                });
                this.loadingOperation.set(null);
            }
        });
    }
}
