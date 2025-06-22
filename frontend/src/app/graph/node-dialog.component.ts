import { Component, computed, effect, inject } from '@angular/core';
import { DialogModule } from 'primeng/dialog';
import { GraphStore } from './graph.store';
import { NodeCardComponent } from './node-dialog-card.component';
import { AuthorData, JournalData, PaperData, PublicationVenueData, DocumentData } from './types';
import { DividerModule } from 'primeng/divider';
import { environment } from "src/environments/environment";

@Component({
    imports: [DialogModule, NodeCardComponent, DividerModule],
    selector: 'app-node-dialog',
    template: `
    <p-dialog
      [(visible)]="visible"
      [modal]="true"
      [style]="{ width: '50vw', height: '80vh' }"
      (visibleChange)="onVisibleChange($event)">
      <div class="flex p-4 flex-col w-full">
        @if (selectedLabel() === 'Author') {
            <p class="text-xl bold">Author Details</p>
            <p-divider />
            <app-node-card header="Name" [body]="selectedAuthor().name"></app-node-card>
            <p-divider />
            <app-node-card header="Paper Count" [body]="selectedAuthor()?.paper_count"></app-node-card>
            <p-divider />
            <app-node-card header="Citation Count" [body]="selectedAuthor()?.citation_count"></app-node-card>
            <p-divider />
            <app-node-card header="H-Index" [body]="selectedAuthor()?.h_index"></app-node-card>
            <p-divider />
        } @else if (selectedLabel() === 'Paper') {
            <p class="text-xl bold">Paper Details</p>
            <p-divider />
            <app-node-card header="Title" [body]="selectedPaper()?.title"></app-node-card>
            <p-divider />
            <app-node-card header="Abstract" [body]="selectedPaper()?.abstract"></app-node-card>
            <p-divider />
            <app-node-card header="Publication Date" [body]="selectedPaper()?.publication_date"></app-node-card>
            <p-divider />
            <app-node-card header="Citation Count" [body]="selectedPaper()?.citation_count"></app-node-card>
            <p-divider />
            <app-node-card header="Paper Id" [body]="selectedPaper()?.paper_id"></app-node-card>
            <p-divider />
        } @else if (selectedLabel() === 'Journal') {
          <p class="text-xl bold">Journal Details</p>
          <p-divider />
          <app-node-card header="Name" [body]="selectedJournal()?.name"></app-node-card>
          <p-divider />
        } @else if (selectedLabel() === 'PublicationVenue') {
          <p class="text-xl bold">Publication Venue Details</p>
          <p-divider />
          <app-node-card header="Name" [body]="selectedPublicationVenue()?.name"></app-node-card>
          <p-divider />
          <app-node-card header="Type" [body]="selectedPublicationVenue()?.type"></app-node-card>
          <p-divider />
          <app-node-card header="URL" [body]="selectedPublicationVenue()?.url"></app-node-card>
          <p-divider />
        } @else if (selectedLabel() === 'Document') {
          <p class="text-xl bold">Document Details</p>
          <p-divider />
          <app-node-card header="Name" [body]="selectedDocument()?.name"></app-node-card>
          <p-divider />
          <app-node-card header="File Name" [body]="selectedDocument()?.og_path"></app-node-card>
          <p-divider />
          <div class="flex align-items-center gap-2">
            <i class="pi pi-file text-primary"></i>
            <a 
              [href]="getDocumentUrl(selectedDocument()?.og_path)" 
              target="_blank" 
              rel="noopener noreferrer"
              class="text-primary hover:text-primary-600 underline cursor-pointer">
              Open Document
            </a>
          </div>
        }
      </div>
    </p-dialog>
  `
})
export class NodeDialogComponent {
  state = inject(GraphStore);
  visible = this.state.showNodeDialog;

  selectedLabel = computed(() => this.state.selectedNode()?.label ?? '');
  selectedAuthor = computed(() => this.state.selectedNode()?.properties as AuthorData);
  selectedPaper = computed(() => this.state.selectedNode()?.properties as PaperData);
  selectedJournal = computed(() => this.state.selectedNode()?.properties as JournalData);
  selectedPublicationVenue = computed(() => this.state.selectedNode()?.properties as PublicationVenueData);
  selectedDocument = computed(() => this.state.selectedNode()?.properties as DocumentData);

  onVisibleChange(visible: boolean) {
    this.visible.set(visible);
  }

  getDocumentUrl(path: string | undefined): string {
    if (!path) return '';
    return `${environment.apiBaseUrl}/docs/${path}`;
  }
}
