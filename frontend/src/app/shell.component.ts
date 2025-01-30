import { Component, inject, model, ViewEncapsulation } from '@angular/core';
import { CommonModule } from '@angular/common';
import { GraphStore } from './graph/graph.store';
import { GraphComponent } from './graph/graph.component';

@Component({
  selector: 'app-shell',
  imports: [CommonModule, GraphComponent],
  template: `
    <app-graph class="h-screen w-full" />
  `,
  styles: [],
  encapsulation: ViewEncapsulation.None,
})
export class ShellComponent {
  graphStore = inject(GraphStore);
}
