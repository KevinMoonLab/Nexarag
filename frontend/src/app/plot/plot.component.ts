import { Component, computed, effect, ElementRef, inject, model, OnDestroy, OnInit, signal, viewChild, ViewEncapsulation } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ButtonModule } from 'primeng/button';
import { PlotlyModule } from 'angular-plotly.js';

import Plotly from 'plotly.js-dist-min';
import { ViewportStore } from '../viewport/viewport.store';
import { SplitterModule } from 'primeng/splitter';
import { PlotControlComponent } from "./plot-controls.component";
import { EventService } from '../events.service';

export type RawPlotData = {
  embeddings: number[][];
  labels: string[];
  paper_ids: string[];
}

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
  #events = inject(EventService);
  logger = effect(() => console.log('Plot data:', this.plotData()));

  constructor() {
    this.#events.events$.subscribe((event) => {
      if (event.type === 'plot_created') {
        const mappedData = this.transformEmbeddingDataToPlot(event.body as RawPlotData);
        this.plotData.set(mappedData);
      }
    });
  }

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
  plotData = signal<PlotData>(defaultPlot);
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

  private transformEmbeddingDataToPlot(data: RawPlotData): PlotData {
    const x = data.embeddings.map(e => e[0]);
    const y = data.embeddings.map(e => e[1]);
  
    const categories = Array.from(new Set(data.labels));
    const categoryIndices = data.labels.map(label => categories.indexOf(label));
  
    return {
      x,
      y,
      nodeIds: data.paper_ids,
      marker: {
        color: categoryIndices,
        colorscale: 'Category10', // Plotly categorical scale
        size: 10,
        showscale: true,
        colorbar: {
          title: 'Label',
          tickvals: categories.map((_, i) => i),
          ticktext: categories,
        }
      },
      title: 'PCA of Abstract Embeddings',
      xTitle: 'Principal Component 1',
      yTitle: 'Principal Component 2',
    };
  }
}