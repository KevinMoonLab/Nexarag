import { Component, computed, inject } from '@angular/core';
import { DialogModule } from 'primeng/dialog';
import { GraphStore } from './graph.store';
import { NodeCardComponent } from './node-dialog-card.component';
import { AuthorData, PaperData } from './types';
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
            <p-divider />
            <app-node-card header="Name" [body]="selectedAuthor()?.name"></app-node-card>
            <p-divider />
            <app-node-card header="Author Id" [body]="selectedAuthor()?.authorId"></app-node-card>
            <p-divider />
        } @else {
            <p-divider />
            <app-node-card header="Title" [body]="selectedPaper()?.title"></app-node-card>
            <p-divider />
            <app-node-card header="Abstract" [body]="selectedPaper()?.abstract"></app-node-card>
            <p-divider />
            <app-node-card header="Publication Date" [body]="selectedPaper()?.publicationDate"></app-node-card>
            <p-divider />
            <app-node-card header="Citation Count" [body]="selectedPaper()?.citationCount"></app-node-card>
            <p-divider />
            <app-node-card header="Level" [body]="selectedPaper()?.level"></app-node-card>
            <p-divider />
            <app-node-card header="Paper Id" [body]="selectedPaper()?.paperId"></app-node-card>
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

  onVisibleChange(visible: boolean) {
    this.visible.set(visible);
  }
}
