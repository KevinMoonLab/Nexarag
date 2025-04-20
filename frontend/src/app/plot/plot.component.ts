import { Component, computed, effect, ElementRef, inject, model, viewChild, ViewEncapsulation } from '@angular/core';
import { CommonModule } from '@angular/common';
import { InputTextModule } from 'primeng/inputtext';
import { FormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { SplitterModule } from 'primeng/splitter';

@Component({
  selector: 'app-plot',
  imports: [CommonModule, InputTextModule, FormsModule, ButtonModule, SplitterModule],
  template: `
        Hello world
    `,
  styles: [],
  encapsulation: ViewEncapsulation.None,
})
export class PlotComponent {
    
}
