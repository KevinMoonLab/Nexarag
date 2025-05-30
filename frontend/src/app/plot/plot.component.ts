import { Component, computed, effect, ElementRef, inject, model, OnDestroy, OnInit, signal, viewChild, ViewEncapsulation } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ButtonModule } from 'primeng/button';
import { PlotlyModule } from 'angular-plotly.js';

import Plotly from 'plotly.js-dist-min';
import { SplitterModule } from 'primeng/splitter';
import { PlotControlComponent } from "./plot-controls.component";
import { EventService } from '../events.service';
import { GraphStore } from '../graph/graph.store';

export type RawPlotData = {
  embeddings: number[][];
  labels: string[];
  paper_ids: string[];
}

export type PlotData = {
  x: number[];
  y: number[];
  id: string[];
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
  x: [],
  y: [],
  id: [],
  marker: {
    color: [],
    colorscale: 'Viridis',
    colorbar: {
      title: 'Date',
      tickvals: [],
      ticktext: []
    },
    showscale: true,
    size: 12,
  },
  nodeIds: [],
  title: 'No Data Selected',
  xTitle: 'Component 2',
  yTitle: 'Component 1',
};

@Component({
  selector: 'app-plot',
  standalone: true,
  imports: [CommonModule, PlotlyModule, SplitterModule, PlotControlComponent],
  template: `
    <p-splitter class="flex-grow h-full w-full" layout="vertical" panelStyleClass="h-screen" [panelSizes]="[50, 50]">
      <ng-template #panel>
        <div class="p-8 flex-grow h-full w-full">
          <plotly-plot
            #plot
            (plotlyClick)="handleClick($event)"
            [data]="plotlyData().data"
            [layout]="plotlyData().layout">
          </plotly-plot>
        </div>
      </ng-template>
      <ng-template #panel>
        <div class="p-12 h-full w-full overflow-y-auto">
          <app-plot-controls class="min-h-full" />
        </div>
      </ng-template>
    </p-splitter>
  `,
  encapsulation: ViewEncapsulation.None,
})
export class PlotComponent implements OnInit {
  plotEl = viewChild('plot', { read: ElementRef });
  graphStore = inject(GraphStore);
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
    this.graphStore.plotResize.subscribe(() => {
      this.resizePlot();
    });
  }

  handleClick(event: any) {
    if (event.points.length == 0) {
      return;
    }
    const point = event.points[0];
    const pointIndex = point.pointIndex;
    const pointId = point.data.id[pointIndex];
    this.graphStore.setSelectedPaper(pointId);
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
      id: this.plotData().id,
      type: 'scatter',
      mode: 'markers',
      marker: this.plotData().marker
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
    const coords = data.embeddings.map(e => e.slice(0, 2));
    const x = coords.map(c => c[0]);
    const y = coords.map(c => c[1]);

    const categories = Array.from(new Set(data.labels));

    const PALETTE20 = [
      '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
      '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
      '#aec7e8', '#ffbb78', '#98df8a', '#ff9896', '#c5b0d5',
      '#c49c94', '#f7b6d2', '#c7c7c7', '#dbdb8d', '#9edae5'
    ];

    // Shuffle colors (optional if you want randomized mapping)
    const shuffled = [...categories].sort(() => Math.random() - 0.5);

    const labelToIndex = new Map<string, number>();
    shuffled.forEach((label, index) => labelToIndex.set(label, index));

    const categoryIndices = data.labels.map(label => labelToIndex.get(label)!);

    // Generate custom colorscale
    const colorscale = shuffled.map((_, i) => [
      i / Math.max(1, shuffled.length - 1),
      PALETTE20[i % PALETTE20.length]
    ]);

    console.log('x:', x);
    console.log('y:', y);
    console.log('Categories:', categoryIndices);
    console.log('Colorscale:', colorscale);

    return {
      x,
      y,
      id: data.paper_ids,
      nodeIds: data.paper_ids,
      marker: {
        color: categoryIndices,
        colorscale: colorscale,
        size: 10,
        showscale: true,
        cmin: 0,
        cmax: shuffled.length - 1,
        colorbar: {
          title: 'Label',
          tickvals: shuffled.map((_, i) => i),
          ticktext: shuffled,
        }
      } as any,

      title: 'PCA of Abstract Embeddings',
      xTitle: 'Principal Component 1',
      yTitle: 'Principal Component 2'
    };
  }
}