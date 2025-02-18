import { Component, ViewEncapsulation } from '@angular/core';
import { CommonModule } from '@angular/common';
import { GraphComponent } from './graph/graph.component';
import { ToastComponent } from './toast/toast.component';

@Component({
  selector: 'app-shell',
  imports: [CommonModule, GraphComponent, ToastComponent],
  template: `
    <app-graph class="h-screen w-full" />
    <app-toast />
  `,
  styles: [],
  encapsulation: ViewEncapsulation.None,
})
export class ShellComponent {
}
