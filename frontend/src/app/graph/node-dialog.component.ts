import { Component, computed, effect, inject } from '@angular/core';
import { DialogModule } from 'primeng/dialog';
import { GraphStore } from './graph.store';
import { NodeCardComponent } from './node-dialog-card.component';
import { AuthorData, JournalData, PaperData, PublicationVenueData } from './types';
import { DividerModule } from 'primeng/divider';

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

  onVisibleChange(visible: boolean) {
    this.visible.set(visible);
  }
}
