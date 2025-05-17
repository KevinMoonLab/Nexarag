import { Component, computed, effect, ElementRef, inject, model, OnDestroy, OnInit, signal, viewChild, ViewEncapsulation } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ButtonModule } from 'primeng/button';
import { PlotlyModule } from 'angular-plotly.js';

import Plotly from 'plotly.js-dist-min';
import { ViewportStore } from '../viewport/viewport.store';
import { SplitterModule } from 'primeng/splitter';
import { PlotControlComponent } from "./plot-controls.component";

export type PlotData = {
  x: number[];
  y: number[];
  marker: {
    color: any[];
    colorscale?: string;
    colorbar?: {
      title: string;
      tickvals: number[];
      ticktext: string[];
    };
    size: number;
    showscale?: true;
  };
  nodeIds: string[];
  title: string;
  xTitle: string;
  yTitle: string;
};

const defaultPlot: PlotData = {
  x: [0, 1, 2, 3],
  y: [0, 1, 2, 3],
  marker: {
    color: [
      new Date('2024-01-01').getTime(),
      new Date('2024-02-01').getTime(),
      new Date('2024-03-01').getTime(),
      new Date('2024-04-01').getTime()
    ],
    colorscale: 'Viridis',
    colorbar: {
      title: 'Date',
      tickvals: [
        new Date('2024-01-01').getTime(),
        new Date('2024-02-01').getTime(),
        new Date('2024-03-01').getTime(),
        new Date('2024-04-01').getTime()
      ],
      ticktext: [
        'Jan 1', 'Feb 1', 'Mar 1', 'Apr 1'
      ]
    },
    showscale: true,
    size: 12,
  },
  nodeIds: [],
  title: 'PCA Embedding Components',
  xTitle: 'Component 2',
  yTitle: 'Component 1',
};

@Component({
  selector: 'app-plot',
  standalone: true,
  imports: [CommonModule, PlotlyModule, SplitterModule, PlotControlComponent],
  template: `
    <p-splitter class="flex-grow h-full w-full" layout="vertical" panelStyleClass="h-screen" [panelSizes]="[60, 40]">
      <ng-template #panel>
        <div class="flex-grow h-full w-full">
          <plotly-plot
            #plot
            [data]="plotlyData().data"
            [layout]="plotlyData().layout">
          </plotly-plot>
        </div>
      </ng-template>
      <ng-template #panel>
        <div class="h-full w-full overflow-y-auto">
          <app-plot-controls class="min-h-full" />
        </div>
      </ng-template>
    </p-splitter>
  `,
  encapsulation: ViewEncapsulation.None,
})
export class PlotComponent implements OnInit {
  plotEl = viewChild('plot', { read: ElementRef });
  viewportStore = inject(ViewportStore);

  ngOnInit() {
    this.viewportStore.plotResize.subscribe(() => {
      console.log('Plot resize event triggered');
      this.resizePlot();
    });
  }

  resizePlot() {
    const plot = this.plotEl()?.nativeElement;
    if (plot) {
      setTimeout(() => {
        Plotly.Plots.resize(plot);
      }, 30);
    }
  }
  plotData = signal(defaultPlot)
  plotlyData = computed(() => ({
    data: [{
      x: this.plotData().x,
      y: this.plotData().y,
      type: 'scatter',
      mode: 'markers',
      marker: this.plotData().marker,
    }],
    layout: {
      title: { text: this.plotData().title },
      xaxis: { title: { text: this.plotData().xTitle } },
      yaxis: { title: { text: this.plotData().yTitle } }
    },
    config: {
      responsive: true
    }
  }));
}