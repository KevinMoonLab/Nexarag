import { Component, computed, effect, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { GraphStore } from '../graph/graph.store';


@Component({
    imports: [CommonModule],
    selector: 'app-projects',
    template: `Hello world!`
})
export class ProjectsComponent {
  state = inject(GraphStore);

}
