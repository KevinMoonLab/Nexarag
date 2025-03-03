import { Component, computed, effect, inject } from '@angular/core';
import { DialogModule } from 'primeng/dialog';
import { DividerModule } from 'primeng/divider';
import { GraphStore } from './graph.store';
import { FileUploadModule, UploadEvent } from 'primeng/fileupload';
import { CommonModule } from '@angular/common';
import { PaperData } from './types';
import { environment } from 'src/environments/environment';
import { HttpClient } from '@angular/common/http';
import { ToastService } from '../toast/toast.service';

@Component({
    imports: [CommonModule, DialogModule, DividerModule, FileUploadModule, DividerModule],
    selector: 'app-doc-dialog',
    template: `<p-dialog
      [(visible)]="visible"
      [modal]="true"
      [style]="{ width: '50vw', height: '80vh' }"
      (visibleChange)="onVisibleChange($event)">
    <p class="text-xl bold">Add documents for '{{ selectedNode()?.title ?? 'No title' }}'</p>
    <p-divider />
    <p-fileUpload  
      (onUpload)="onUpload($event)" 
      [multiple]="false" 
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
    </p-fileUpload>
  </p-dialog>`
})
export class DocumentDialogComponent {
  #toast = inject(ToastService);
  state = inject(GraphStore);
  visible = this.state.showDocumentDialog;
  selectedNode = computed(() => this.state.selectedNode()?.properties as PaperData ?? null);
  uploadedFiles: any[] = [];

  onVisibleChange(visible: boolean) {
    this.visible.set(visible);
  }

  onUpload(event: any) {
      this.#toast.show('Files uploaded successfully.');
      this.uploadedFiles = [];
      this.visible.set(false);
  }

  url = computed(() => environment.apiBaseUrl + '/docs/upload/' + (this.selectedNode()?.paper_id ?? ''));
}
