import { Component, inject, signal, ViewEncapsulation } from '@angular/core';
import { CommonModule } from '@angular/common';
import { InputTextModule } from 'primeng/inputtext';
import { FormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { ChatMenuComponent } from "../chat/chat-menu.component";
import { MenuComponent } from "../menu/menu.component";
import { SplitterModule } from 'primeng/splitter';
import { GraphComponent } from "../graph/graph.component";
import { PlotComponent } from "../plot/plot.component";
import { ViewportStore } from './viewport.store';

@Component({
  selector: 'app-viewport',
  imports: [CommonModule, InputTextModule, FormsModule, ButtonModule, SplitterModule, ChatMenuComponent, MenuComponent, GraphComponent, PlotComponent],
  template: `
        <div class="relative h-screen w-full flex">
          <div class="absolute top-0 left-0 h-full z-50">
            <app-menu />
          </div>
          <div class="absolute top-0 right-0 h-full z-50">
            <app-chat-menu />
          </div>
          @if (viewportStore.showPlot()) {
            <p-splitter (onResizeEnd)="onSplitterResize($event)" class="flex-grow h-full w-full pl-10" panelStyleClass="h-screen">
              <ng-template #panel>
                <app-plot class="flex-grow h-screen w-full" />
              </ng-template>
              <ng-template #panel>
                <app-graph class="flex-grow h-screen w-full" />
              </ng-template>
            </p-splitter>
          } @else {
            <app-graph class="flex-grow h-screen w-full" />
          }
        </div>
        
    `,
  styles: [],
  encapsulation: ViewEncapsulation.None,
})
export class ViewportComponent {
  viewportStore = inject(ViewportStore);

  onSplitterResize(evt:any) {
    this.viewportStore.emitPlotResize();
  }
}
