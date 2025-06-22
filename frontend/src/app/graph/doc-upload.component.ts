import { Component, computed, effect, inject, output } from '@angular/core';
import { DialogModule } from 'primeng/dialog';
import { DividerModule } from 'primeng/divider';
import { GraphStore } from './graph.store';
import { FileUploadModule } from 'primeng/fileupload';
import { CommonModule } from '@angular/common';
import { PaperData } from './types';
import { environment } from 'src/environments/environment';
import { ToastService } from '../toast/toast.service';

@Component({
    imports: [CommonModule, DialogModule, DividerModule, FileUploadModule, DividerModule],
    selector: 'app-doc-upload',
    template: `
    <p class="text-xl bold">{{ selectedNode() ? 'Add documents for ' + selectedNode().title : 'Upload documents' }}</p>
    <p-divider />
    <p-fileUpload  
      (onUpload)="onUpload($event)" 
      [multiple]="selectedNode() == null" 
      [url]="url()"
      accept=".md,.txt,.pdf" 
      maxFileSize="100000000" 
      name="docs"
      mode="advanced">
        <ng-template #empty>
            <div>Drag and drop files to here to upload.</div>
        </ng-template>
        <ng-template #content>
            <ul *ngIf="uploadedFiles.length">
                <li *ngFor="let file of uploadedFiles">{{ file.name }} - {{ file.size }} bytes</li>
            </ul>
        </ng-template>
    </p-fileUpload>`
})
export class DocumentUploadComponent {
  #toast = inject(ToastService);
  state = inject(GraphStore);
  selectedNode = computed(() => this.state.selectedNode()?.properties as PaperData ?? null);
  uploadedFiles: any[] = [];
  onUploadedFiles = output<any>();

  onUpload(event: any) {
      this.#toast.show('Files uploaded successfully.');
      this.uploadedFiles = [];
      this.onUploadedFiles.emit(event);
  }

  url = computed(() => {
    const selectedNode = this.selectedNode();
    const baseUrl = environment.apiBaseUrl;
    
    if (selectedNode?.paper_id) {
      return `${baseUrl}/docs/upload/${selectedNode.paper_id}`;
    } else {
      return `${baseUrl}/docs/bulk/upload/`;
    }
  });
}
