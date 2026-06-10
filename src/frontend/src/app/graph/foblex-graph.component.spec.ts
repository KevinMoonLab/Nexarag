import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { FoblexGraphComponent } from './foblex-graph.component';
import { GraphLayoutService } from './graph-layout.service';
import { GraphStore } from './graph.store';
import { ToastService } from '../toast/toast.service';
import { EventService, Event } from '../events.service';
import { KnowledgeNode, Edge } from './types';
import { Subject } from 'rxjs';
import { NO_ERRORS_SCHEMA } from '@angular/core';

// --- Helpers ---

function makePaperNode(id: string, title: string): KnowledgeNode {
  return {
    id,
    label: 'Paper',
    properties: {
      title,
      paper_id: `pid-${id}`,
      citation_count: 10,
      influential_citation_count: 2,
      reference_count: 5,
      year: 2023,
      publication_date: '2023-01-01',
      publication_types: 'JournalArticle',
    },
  };
}

function makeAuthorNode(id: string, name: string): KnowledgeNode {
  return {
    id,
    label: 'Author',
    properties: {
      name,
      author_id: `aid-${id}`,
      citation_count: 100,
      h_index: 20,
      affiliations: 'MIT',
      url: '',
      paper_count: 50,
    },
  };
}

function makeJournalNode(id: string, name: string): KnowledgeNode {
  return {
    id,
    label: 'Journal',
    properties: { name, volume: '1', pages: '1-10' },
  };
}

function makeDocumentNode(id: string, name: string): KnowledgeNode {
  return {
    id,
    label: 'Document',
    properties: { name, path: `/docs/${id}`, og_path: `/og/${id}` },
  };
}

function makePubVenueNode(id: string, name: string): KnowledgeNode {
  return {
    id,
    label: 'PublicationVenue',
    properties: {
      name,
      alternate_names: '',
      alternate_urls: '',
      type: 'conference',
      url: '',
      venue_id: `vid-${id}`,
    },
  };
}

function makeEdge(source: string, target: string): Edge {
  return { source, target, type: 'AUTHORED', properties: {} };
}

describe('FoblexGraphComponent', () => {
  let component: FoblexGraphComponent;
  let graphStore: GraphStore;
  let httpMock: HttpTestingController;
  let eventsSubject: Subject<Event>;

  beforeEach(() => {
    eventsSubject = new Subject<Event>();

    // Stub the ELK layout so no real engine runs in jsdom; this also removes the
    // component's provideFLayout/ElkLayoutEngine wiring for the unit test.
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule, FoblexGraphComponent],
      providers: [
        GraphStore,
        ToastService,
        {
          provide: EventService,
          useValue: { events$: eventsSubject.asObservable() },
        },
      ],
      schemas: [NO_ERRORS_SCHEMA],
    });

    TestBed.overrideComponent(FoblexGraphComponent, {
      set: {
        providers: [
          { provide: GraphLayoutService, useValue: { layout: async () => new Map() } },
        ],
      },
    });

    httpMock = TestBed.inject(HttpTestingController);
    graphStore = TestBed.inject(GraphStore);

    // Flush constructor fetchGraph
    const req = httpMock.expectOne((r) => r.url.includes('/graph/get/'));
    req.flush({ nodes: [], edges: [] });

    const fixture = TestBed.createComponent(FoblexGraphComponent);
    component = fixture.componentInstance;
  });

  afterEach(() => {
    httpMock.verify();
  });

  // --- node colors (via displayNodes) ---

  describe('displayNodes colors', () => {
    it('should assign red (#D72638) to Author nodes', () => {
      graphStore.graph.set({ nodes: [makeAuthorNode('a1', 'Alice')], edges: [] });
      expect(component.displayNodes()[0].color).toBe('#D72638');
    });

    it('should assign blue (#3E92CC) to Paper nodes', () => {
      graphStore.graph.set({ nodes: [makePaperNode('p1', 'Test')], edges: [] });
      expect(component.displayNodes()[0].color).toBe('#3E92CC');
    });

    it('should assign green (#6BBF59) to Journal nodes', () => {
      graphStore.graph.set({ nodes: [makeJournalNode('j1', 'Nature')], edges: [] });
      expect(component.displayNodes()[0].color).toBe('#6BBF59');
    });

    it('should assign orange (#F4A261) to PublicationVenue nodes', () => {
      graphStore.graph.set({ nodes: [makePubVenueNode('v1', 'NeurIPS')], edges: [] });
      graphStore.selectedDisplayFilters.set(['PublicationVenue']);
      expect(component.displayNodes()[0].color).toBe('#F4A261');
    });

    it('should assign purple (#8E44AD) to Document nodes', () => {
      graphStore.graph.set({ nodes: [makeDocumentNode('d1', 'notes.pdf')], edges: [] });
      expect(component.displayNodes()[0].color).toBe('#8E44AD');
    });
  });

  // --- name truncation (via displayNodes) ---

  describe('displayNodes names', () => {
    it('should show the full node name without truncation', () => {
      const longTitle = 'A Very Long Paper Title That Exceeds Thirty Characters Easily';
      graphStore.graph.set({ nodes: [makePaperNode('p1', longTitle)], edges: [] });
      expect(component.displayNodes()[0].name).toBe(longTitle);
    });

    it('should show short names verbatim', () => {
      graphStore.graph.set({ nodes: [makePaperNode('p1', 'Short Title')], edges: [] });
      expect(component.displayNodes()[0].name).toBe('Short Title');
    });
  });

  // --- renderEdges ---

  describe('renderEdges', () => {
    it('should map edges with source and target', () => {
      graphStore.graph.set({
        nodes: [makePaperNode('p1', 'P'), makeAuthorNode('a1', 'A')],
        edges: [makeEdge('a1', 'p1')],
      });

      const edges = component.renderEdges();
      expect(edges).toHaveLength(1);
      expect(edges[0].source).toBe('a1');
      expect(edges[0].target).toBe('p1');
    });

    it('should produce a unique id per edge', () => {
      graphStore.graph.set({
        nodes: [makeAuthorNode('a1', 'A'), makePaperNode('p1', 'P'), makePaperNode('p2', 'P2')],
        edges: [makeEdge('a1', 'p1'), makeEdge('a1', 'p2')],
      });

      const ids = component.renderEdges().map((e) => e.id);
      expect(new Set(ids).size).toBe(2);
    });

    it('should handle empty graph', () => {
      graphStore.graph.set({ nodes: [], edges: [] });
      expect(component.displayNodes()).toEqual([]);
      expect(component.renderEdges()).toEqual([]);
    });
  });

  // --- node sizing ---

  describe('displayNodes layout footprint', () => {
    it('should use a fixed footprint when weightNodes is false', () => {
      graphStore.weightNodes.set(false);
      graphStore.graph.set({ nodes: [makeAuthorNode('a1', 'Alice')], edges: [] });
      const node = component.displayNodes()[0];
      expect(node.width).toBe(190);
      expect(node.height).toBe(70);
    });

    it('should give higher-degree nodes at least as large a footprint when weighted', () => {
      graphStore.weightNodes.set(true);
      const a = makeAuthorNode('a1', 'Alice');
      const p1 = makePaperNode('p1', 'P1');
      const p2 = makePaperNode('p2', 'P2');
      graphStore.graph.set({
        nodes: [a, p1, p2],
        edges: [makeEdge('a1', 'p1'), makeEdge('a1', 'p2')],
      });

      const nodes = component.displayNodes();
      const author = nodes.find((n) => n.id === 'a1')!;
      const paper = nodes.find((n) => n.id === 'p1')!;
      expect(author.width).toBeGreaterThanOrEqual(paper.width);
    });
  });

  // --- context-menu selection ---

  describe('context menu selection', () => {
    it('should set the selected node key on node right-click', () => {
      const event = { preventDefault: () => {}, stopPropagation: () => {} } as MouseEvent;
      component.onNodeContext(event, 'a1');
      expect(graphStore.selectedNodeKey()).toBe('a1');
    });

    it('should clear the selected node key on canvas right-click', () => {
      graphStore.selectedNodeKey.set('a1');
      const event = { preventDefault: () => {}, stopPropagation: () => {} } as MouseEvent;
      component.onCanvasContext(event);
      expect(graphStore.selectedNodeKey()).toBe('');
    });
  });
});
