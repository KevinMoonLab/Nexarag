import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { GraphComponent } from './graph.component';
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

describe('GraphComponent', () => {
  let component: GraphComponent;
  let graphStore: GraphStore;
  let httpMock: HttpTestingController;
  let eventsSubject: Subject<Event>;

  beforeEach(() => {
    eventsSubject = new Subject<Event>();

    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule, GraphComponent],
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

    httpMock = TestBed.inject(HttpTestingController);
    graphStore = TestBed.inject(GraphStore);

    // Flush constructor fetchGraph
    const req = httpMock.expectOne((r) => r.url.includes('/graph/get/'));
    req.flush({ nodes: [], edges: [] });

    const fixture = TestBed.createComponent(GraphComponent);
    component = fixture.componentInstance;
  });

  afterEach(() => {
    httpMock.verify();
  });

  // --- getNodeColor (private — tested via cytoscapeGraph computed) ---

  describe('cytoscapeGraph node colors', () => {
    it('should assign red (#D72638) to Author nodes', () => {
      graphStore.graph.set({ nodes: [makeAuthorNode('a1', 'Alice')], edges: [] });
      const nodes = component.cytoscapeGraph().nodes;
      expect(nodes[0].data.color).toBe('#D72638');
    });

    it('should assign blue (#3E92CC) to Paper nodes', () => {
      graphStore.graph.set({ nodes: [makePaperNode('p1', 'Test')], edges: [] });
      const nodes = component.cytoscapeGraph().nodes;
      expect(nodes[0].data.color).toBe('#3E92CC');
    });

    it('should assign green (#6BBF59) to Journal nodes', () => {
      graphStore.graph.set({ nodes: [makeJournalNode('j1', 'Nature')], edges: [] });
      const nodes = component.cytoscapeGraph().nodes;
      expect(nodes[0].data.color).toBe('#6BBF59');
    });

    it('should assign orange (#F4A261) to PublicationVenue nodes', () => {
      graphStore.graph.set({ nodes: [makePubVenueNode('v1', 'NeurIPS')], edges: [] });
      // PublicationVenue is not in default selectedDisplayFilters, add it
      graphStore.selectedDisplayFilters.set(['PublicationVenue']);
      const nodes = component.cytoscapeGraph().nodes;
      expect(nodes[0].data.color).toBe('#F4A261');
    });

    it('should assign purple (#8E44AD) to Document nodes', () => {
      graphStore.graph.set({ nodes: [makeDocumentNode('d1', 'notes.pdf')], edges: [] });
      const nodes = component.cytoscapeGraph().nodes;
      expect(nodes[0].data.color).toBe('#8E44AD');
    });
  });

  // --- truncateName (private — tested via cytoscapeGraph computed) ---

  describe('cytoscapeGraph node name truncation', () => {
    it('should truncate names longer than 30 characters', () => {
      const longTitle = 'A Very Long Paper Title That Exceeds Thirty Characters Easily';
      graphStore.graph.set({ nodes: [makePaperNode('p1', longTitle)], edges: [] });

      const nodes = component.cytoscapeGraph().nodes;
      expect(nodes[0].data.name.length).toBeLessThanOrEqual(33); // 30 + '...'
      expect(nodes[0].data.name).toContain('...');
    });

    it('should not truncate names at or under 30 characters', () => {
      const shortTitle = 'Short Title';
      graphStore.graph.set({ nodes: [makePaperNode('p1', shortTitle)], edges: [] });

      const nodes = component.cytoscapeGraph().nodes;
      expect(nodes[0].data.name).toBe('Short Title');
    });
  });

  // --- cytoscapeGraph computed ---

  describe('cytoscapeGraph', () => {
    it('should map nodes with id, name, color, and weight', () => {
      graphStore.graph.set({
        nodes: [makePaperNode('p1', 'Test Paper'), makeAuthorNode('a1', 'Alice')],
        edges: [makeEdge('a1', 'p1')],
      });

      const result = component.cytoscapeGraph();
      expect(result.nodes).toHaveLength(2);

      const paperNode = result.nodes.find((n) => n.data.id === 'p1');
      expect(paperNode).toBeDefined();
      expect(paperNode!.data.name).toBe('Test Paper');
      expect(paperNode!.data.color).toBe('#3E92CC');
      expect(typeof paperNode!.data.weight).toBe('number');
    });

    it('should map edges with source and target data', () => {
      graphStore.graph.set({
        nodes: [makePaperNode('p1', 'P'), makeAuthorNode('a1', 'A')],
        edges: [makeEdge('a1', 'p1')],
      });

      const result = component.cytoscapeGraph();
      expect(result.edges).toHaveLength(1);
      expect(result.edges[0].data.source).toBe('a1');
      expect(result.edges[0].data.target).toBe('p1');
    });

    it('should compute node weight based on degree and maxDegree', () => {
      const a = makeAuthorNode('a1', 'Alice');
      const p1 = makePaperNode('p1', 'P1');
      const p2 = makePaperNode('p2', 'P2');

      graphStore.graph.set({
        nodes: [a, p1, p2],
        edges: [makeEdge('a1', 'p1'), makeEdge('a1', 'p2')],
      });

      const result = component.cytoscapeGraph();
      const authorNode = result.nodes.find((n) => n.data.id === 'a1');
      const paperNode = result.nodes.find((n) => n.data.id === 'p1');

      // Author has degree 2 (max), paper has degree 1
      // Author weight should be >= paper weight
      expect(authorNode!.data.weight).toBeGreaterThanOrEqual(paperNode!.data.weight);
    });

    it('should handle empty graph', () => {
      graphStore.graph.set({ nodes: [], edges: [] });
      const result = component.cytoscapeGraph();
      expect(result.nodes).toEqual([]);
      expect(result.edges).toEqual([]);
    });
  });

  // --- styleSheet computed ---

  describe('styleSheet', () => {
    it('should include width/height data(weight) when weightNodes is true', () => {
      graphStore.weightNodes.set(true);
      const styles = component.styleSheet() as any[];
      const nodeStyle = styles[0];
      expect(nodeStyle.selector).toBe('node');
      expect(nodeStyle.style['width']).toBe('data(weight)');
      expect(nodeStyle.style['height']).toBe('data(weight)');
    });

    it('should not include width/height when weightNodes is false', () => {
      graphStore.weightNodes.set(false);
      const styles = component.styleSheet() as any[];
      const nodeStyle = styles[0];
      expect(nodeStyle.style['width']).toBeUndefined();
      expect(nodeStyle.style['height']).toBeUndefined();
    });

    it('should always include edge styling', () => {
      const styles = component.styleSheet() as any[];
      const edgeStyle = styles.find((s: any) => s.selector === 'edge');
      expect(edgeStyle).toBeDefined();
      expect(edgeStyle!.style['curve-style']).toBe('bezier');
    });

    it('should always include selected-node styling', () => {
      const styles = component.styleSheet() as any[];
      const selectedStyle = styles.find((s: any) => s.selector === 'node:selected');
      expect(selectedStyle).toBeDefined();
      expect(selectedStyle!.style['border-color']).toBe('#ffa500');
    });
  });
});
