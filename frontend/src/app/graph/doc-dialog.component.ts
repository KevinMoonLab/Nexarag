import { Component, computed, effect, inject } from '@angular/core';
import { DialogModule } from 'primeng/dialog';
import { DividerModule } from 'primeng/divider';
import { GraphStore } from './graph.store';
import { FileUploadModule } from 'primeng/fileupload';
import { CommonModule } from '@angular/common';
import { PaperData } from './types';
import { environment } from 'src/environments/environment';
import { ToastService } from '../toast/toast.service';
import { DocumentUploadComponent } from "./doc-upload.component";

@Component({
    imports: [CommonModule, DialogModule, DividerModule, FileUploadModule, DividerModule, DocumentUploadComponent],
    selector: 'app-doc-dialog',
    template: `<p-dialog
      [(visible)]="visible"
      [modal]="true"
      [style]="{ width: '50vw', height: '80vh' }"
      (visibleChange)="onVisibleChange($event)">
      <app-doc-upload (onUploadedFiles)="handleFileUpload($event)"></app-doc-upload>
  </p-dialog>`
})
export class DocumentDialogComponent {
  state = inject(GraphStore);
  visible = this.state.showDocumentDialog;

  onVisibleChange(visible: boolean) {
    this.visible.set(visible);
  }

  handleFileUpload(event: any) {
    this.visible.set(false);
  }
}
