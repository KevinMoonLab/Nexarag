import { Component, ViewEncapsulation } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ToastComponent } from './toast/toast.component';
import { ViewportComponent } from './viewport/viewport.component';

@Component({
  selector: 'app-shell',
  imports: [CommonModule, ToastComponent, ViewportComponent],
  template: `
    <app-viewport class="h-screen w-full" />
    <app-toast />
  `,
  styles: [],
  encapsulation: ViewEncapsulation.None,
})
export class ShellComponent {
}
