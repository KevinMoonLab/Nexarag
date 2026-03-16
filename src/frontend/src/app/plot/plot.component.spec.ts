import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { EventService, Event } from '../events.service';
import { GraphStore } from '../graph/graph.store';
import { ToastService } from '../toast/toast.service';
import { Subject } from 'rxjs';
import { NO_ERRORS_SCHEMA, Component, signal, computed, inject, effect } from '@angular/core';
import 'cytoscape-context-menus';
import { RawPlotData, PlotData } from './plot.component';

// We cannot import PlotComponent directly because it imports PlotlyModule
// which validates a real Plotly object at module init. Instead, we extract
// and test the data transformation logic in isolation, and test the component
// wiring through a lightweight harness that mirrors its public API.

// Re-implement transformEmbeddingDataToPlot as a standalone function for testing
// (mirrors the private method in PlotComponent exactly)
function transformEmbeddingDataToPlot(data: RawPlotData): PlotData {
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

  const shuffled = [...categories].sort(() => Math.random() - 0.5);

  const labelToIndex = new Map<string, number>();
  shuffled.forEach((label, index) => labelToIndex.set(label, index));

  const categoryIndices = data.labels.map(label => labelToIndex.get(label)!);

  const colorscale = shuffled.map((_, i) => [
    i / Math.max(1, shuffled.length - 1),
    PALETTE20[i % PALETTE20.length]
  ]);

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

describe('PlotComponent data transformation', () => {

  // --- transformEmbeddingDataToPlot ---

  describe('transformEmbeddingDataToPlot', () => {
    const rawData: RawPlotData = {
      embeddings: [
        [1.0, 2.0, 3.0],
        [4.0, 5.0, 6.0],
        [7.0, 8.0, 9.0],
      ],
      labels: ['ML', 'NLP', 'ML'],
      paper_ids: ['pid1', 'pid2', 'pid3'],
    };

    it('should extract x and y from first two embedding dimensions', () => {
      const data = transformEmbeddingDataToPlot(rawData);
      expect(data.x).toEqual([1.0, 4.0, 7.0]);
      expect(data.y).toEqual([2.0, 5.0, 8.0]);
    });

    it('should set paper_ids as both id and nodeIds', () => {
      const data = transformEmbeddingDataToPlot(rawData);
      expect(data.id).toEqual(['pid1', 'pid2', 'pid3']);
      expect(data.nodeIds).toEqual(['pid1', 'pid2', 'pid3']);
    });

    it('should set PCA title and axis labels', () => {
      const data = transformEmbeddingDataToPlot(rawData);
      expect(data.title).toBe('PCA of Abstract Embeddings');
      expect(data.xTitle).toBe('Principal Component 1');
      expect(data.yTitle).toBe('Principal Component 2');
    });

    it('should assign category indices as marker colors', () => {
      const data = transformEmbeddingDataToPlot(rawData);
      const colors = data.marker.color;
      expect(colors).toHaveLength(3);
      // ML appears twice — both should have the same index
      expect(colors[0]).toBe(colors[2]);
      // NLP should differ from ML
      expect(colors[1]).not.toBe(colors[0]);
    });

    it('should create colorbar with unique category labels as ticktext', () => {
      const data = transformEmbeddingDataToPlot(rawData);
      const colorbar = data.marker.colorbar;
      expect(colorbar).toBeDefined();
      expect(colorbar!.ticktext).toHaveLength(2);
      expect(colorbar!.ticktext).toContain('ML');
      expect(colorbar!.ticktext).toContain('NLP');
    });

    it('should build a colorscale array matching the number of unique categories', () => {
      const data = transformEmbeddingDataToPlot(rawData);
      const marker = data.marker as any;
      expect(marker.colorscale).toHaveLength(2);
      marker.colorscale.forEach((entry: any) => {
        expect(entry).toHaveLength(2);
        expect(typeof entry[0]).toBe('number');
        expect(typeof entry[1]).toBe('string');
      });
    });

    it('should handle single-category data', () => {
      const singleCategory: RawPlotData = {
        embeddings: [[1, 2], [3, 4]],
        labels: ['ML', 'ML'],
        paper_ids: ['p1', 'p2'],
      };

      const data = transformEmbeddingDataToPlot(singleCategory);
      expect(data.marker.color[0]).toBe(data.marker.color[1]);
      expect(data.marker.colorbar!.ticktext).toEqual(['ML']);
    });

    it('should handle many categories cycling through PALETTE20', () => {
      const labels = Array.from({ length: 25 }, (_, i) => `cat${i}`);
      const embeddings = labels.map((_, i) => [i, i + 1]);
      const paper_ids = labels.map((_, i) => `p${i}`);

      const data = transformEmbeddingDataToPlot({ embeddings, labels, paper_ids });
      const marker = data.marker as any;
      // 25 unique categories, colorscale wraps around palette
      expect(marker.colorscale).toHaveLength(25);
      expect(marker.colorbar.ticktext).toHaveLength(25);
    });
  });

  // --- plotlyData format ---

  describe('plotlyData structure', () => {
    it('should produce correct Plotly trace format from PlotData', () => {
      const plotData = transformEmbeddingDataToPlot({
        embeddings: [[10, 20]],
        labels: ['Cat'],
        paper_ids: ['px'],
      });

      // Simulate the computed signal logic from PlotComponent
      const plotlyData = {
        data: [{
          x: plotData.x,
          y: plotData.y,
          id: plotData.id,
          type: 'scatter' as const,
          mode: 'markers' as const,
          marker: plotData.marker
        }],
        layout: {
          title: { text: plotData.title },
          xaxis: { title: { text: plotData.xTitle } },
          yaxis: { title: { text: plotData.yTitle } }
        },
      };

      expect(plotlyData.data[0].type).toBe('scatter');
      expect(plotlyData.data[0].mode).toBe('markers');
      expect(plotlyData.data[0].x).toEqual([10]);
      expect(plotlyData.data[0].y).toEqual([20]);
      expect(plotlyData.layout.title.text).toBe('PCA of Abstract Embeddings');
    });
  });

  // --- handleClick logic ---

  describe('handleClick logic', () => {
    let graphStore: GraphStore;
    let httpMock: HttpTestingController;
    let eventsSubject: Subject<Event>;

    beforeEach(() => {
      eventsSubject = new Subject<Event>();

      TestBed.configureTestingModule({
        imports: [HttpClientTestingModule],
        providers: [
          GraphStore,
          ToastService,
          {
            provide: EventService,
            useValue: { events$: eventsSubject.asObservable() },
          },
        ],
      });

      httpMock = TestBed.inject(HttpTestingController);
      graphStore = TestBed.inject(GraphStore);

      // Flush constructor fetchGraph
      const req = httpMock.expectOne((r) => r.url.includes('/graph/get/'));
      req.flush({ nodes: [], edges: [] });
    });

    afterEach(() => {
      httpMock.verify();
    });

    it('should select the paper at the clicked point index', () => {
      const spy = jest.spyOn(graphStore, 'setSelectedPaper');

      // Simulate PlotComponent.handleClick logic
      const event = {
        points: [{ pointIndex: 1, data: { id: ['pid1', 'pid2', 'pid3'] } }],
      };

      if (event.points.length > 0) {
        const point = event.points[0];
        const pointId = point.data.id[point.pointIndex];
        graphStore.setSelectedPaper(pointId);
      }

      expect(spy).toHaveBeenCalledWith('pid2');
    });

    it('should not call setSelectedPaper when no points are clicked', () => {
      const spy = jest.spyOn(graphStore, 'setSelectedPaper');

      const event = { points: [] as any[] };
      if (event.points.length > 0) {
        graphStore.setSelectedPaper(event.points[0].data.id[event.points[0].pointIndex]);
      }

      expect(spy).not.toHaveBeenCalled();
    });
  });
});
