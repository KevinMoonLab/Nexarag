import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { GraphStore } from './graph.store';
import { ToastService } from '../toast/toast.service';
import { EventService } from '../events.service';
import { KnowledgeGraph, KnowledgeNode, Edge } from './types';
import { Subject } from 'rxjs';
import { Event } from '../events.service';
import 'cytoscape-context-menus';

// --- Test fixtures ---

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

function makeEdge(source: string, target: string, type: 'AUTHORED' | 'PUBLISHED_IN' | 'PUBLISHED_AT' | 'BELONGS_TO' = 'AUTHORED'): Edge {
  return { source, target, type, properties: {} };
}

// --- Test suite ---

describe('GraphStore', () => {
  let store: GraphStore;
  let httpMock: HttpTestingController;
  let toastService: ToastService;
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

    store = TestBed.inject(GraphStore);
    httpMock = TestBed.inject(HttpTestingController);
    toastService = TestBed.inject(ToastService);

    // Flush the initial fetchGraph call from the constructor
    const req = httpMock.expectOne((r) => r.url.includes('/graph/get/'));
    req.flush({ nodes: [], edges: [] });
  });

  afterEach(() => {
    httpMock.verify();
  });

  // --- getNodeName ---

  describe('getNodeName', () => {
    it('should return author name', () => {
      expect(store.getNodeName(makeAuthorNode('1', 'Alice'))).toBe('Alice');
    });

    it('should return paper title', () => {
      expect(store.getNodeName(makePaperNode('1', 'Deep Learning'))).toBe('Deep Learning');
    });

    it('should return journal name', () => {
      expect(store.getNodeName(makeJournalNode('1', 'Nature'))).toBe('Nature');
    });

    it('should return publication venue name', () => {
      expect(store.getNodeName(makePubVenueNode('1', 'NeurIPS'))).toBe('NeurIPS');
    });

    it('should return document name', () => {
      expect(store.getNodeName(makeDocumentNode('1', 'notes.pdf'))).toBe('notes.pdf');
    });
  });

  // --- filteredGraph ---

  describe('filteredGraph', () => {
    const paper1 = makePaperNode('p1', 'Graph Neural Networks');
    const paper2 = makePaperNode('p2', 'Transformers');
    const author1 = makeAuthorNode('a1', 'Alice');
    const edge1 = makeEdge('a1', 'p1');
    const edge2 = makeEdge('a1', 'p2');

    beforeEach(() => {
      store.graph.set({
        nodes: [paper1, paper2, author1],
        edges: [edge1, edge2],
      });
    });

    it('should return all nodes when no search term and all types selected', () => {
      const filtered = store.filteredGraph();
      expect(filtered.nodes).toHaveLength(3);
      expect(filtered.edges).toHaveLength(2);
    });

    it('should filter nodes by search term (case-insensitive)', () => {
      store.searchTerm.set('graph');
      const filtered = store.filteredGraph();
      expect(filtered.nodes).toHaveLength(1);
      expect(filtered.nodes[0].id).toBe('p1');
    });

    it('should filter nodes by selected display filters', () => {
      store.selectedDisplayFilters.set(['Paper']);
      const filtered = store.filteredGraph();
      expect(filtered.nodes).toHaveLength(2);
      expect(filtered.nodes.every((n) => n.label === 'Paper')).toBe(true);
    });

    it('should exclude edges whose source or target is filtered out', () => {
      store.selectedDisplayFilters.set(['Paper']);
      const filtered = store.filteredGraph();
      // Both edges reference author a1, which is filtered out
      expect(filtered.edges).toHaveLength(0);
    });

    it('should return edges only when both endpoints are visible', () => {
      store.selectedDisplayFilters.set(['Paper', 'Author']);
      const filtered = store.filteredGraph();
      expect(filtered.edges).toHaveLength(2);
    });

    it('should combine search term and type filter', () => {
      store.selectedDisplayFilters.set(['Paper']);
      store.searchTerm.set('transformers');
      const filtered = store.filteredGraph();
      expect(filtered.nodes).toHaveLength(1);
      expect(filtered.nodes[0].id).toBe('p2');
    });

    it('should return empty graph when no types match', () => {
      store.selectedDisplayFilters.set(['PublicationVenue']);
      const filtered = store.filteredGraph();
      expect(filtered.nodes).toHaveLength(0);
      expect(filtered.edges).toHaveLength(0);
    });
  });

  // --- degreeMap and maxDegree ---

  describe('degreeMap / maxDegree', () => {
    it('should compute degree from parent and child relationships', () => {
      const a = makeAuthorNode('a1', 'Alice');
      const p1 = makePaperNode('p1', 'Paper 1');
      const p2 = makePaperNode('p2', 'Paper 2');
      store.graph.set({
        nodes: [a, p1, p2],
        edges: [makeEdge('a1', 'p1'), makeEdge('a1', 'p2')],
      });

      const degrees = store.degreeMap();
      expect(degrees.get('a1')).toBe(2); // two children
      expect(degrees.get('p1')).toBe(1); // one parent
      expect(degrees.get('p2')).toBe(1); // one parent
    });

    it('should count unique neighbors only', () => {
      const a = makeAuthorNode('a1', 'Alice');
      const p = makePaperNode('p1', 'Paper');
      // Two edges between same pair
      store.graph.set({
        nodes: [a, p],
        edges: [makeEdge('a1', 'p1'), makeEdge('a1', 'p1')],
      });

      expect(store.degreeMap().get('a1')).toBe(1);
      expect(store.degreeMap().get('p1')).toBe(1);
    });

    it('should return 0 degree for isolated nodes', () => {
      store.graph.set({
        nodes: [makePaperNode('p1', 'Lonely')],
        edges: [],
      });
      expect(store.degreeMap().get('p1')).toBe(0);
    });

    it('should compute maxDegree correctly', () => {
      const a = makeAuthorNode('a1', 'Alice');
      const p1 = makePaperNode('p1', 'P1');
      const p2 = makePaperNode('p2', 'P2');
      const p3 = makePaperNode('p3', 'P3');
      store.graph.set({
        nodes: [a, p1, p2, p3],
        edges: [makeEdge('a1', 'p1'), makeEdge('a1', 'p2'), makeEdge('a1', 'p3')],
      });
      expect(store.maxDegree()).toBe(3);
    });
  });

  // --- graphNodeRepresentations (nodeMap, typeMap, childMap, parentMap) ---

  describe('graphNodeRepresentations', () => {
    const a = makeAuthorNode('a1', 'Alice');
    const p1 = makePaperNode('p1', 'Paper 1');
    const p2 = makePaperNode('p2', 'Paper 2');
    const j = makeJournalNode('j1', 'Nature');

    beforeEach(() => {
      store.graph.set({
        nodes: [a, p1, p2, j],
        edges: [makeEdge('a1', 'p1'), makeEdge('a1', 'p2'), makeEdge('p1', 'j1', 'PUBLISHED_IN')],
      });
    });

    it('should build nodeMap with all nodes indexed by id', () => {
      const nm = store.nodeMap();
      expect(nm.size).toBe(4);
      expect(nm.get('a1')).toEqual(a);
      expect(nm.get('p1')).toEqual(p1);
    });

    it('should build typeMap grouping nodes by label', () => {
      const tm = store.typeMap();
      expect(tm.get('Author')).toHaveLength(1);
      expect(tm.get('Paper')).toHaveLength(2);
      expect(tm.get('Journal')).toHaveLength(1);
    });

    it('should build childMap from edges (source → target nodes)', () => {
      const cm = store.childMap();
      expect(cm.get('a1')).toHaveLength(2);
      expect(cm.get('a1')?.map((n) => n.id).sort()).toEqual(['p1', 'p2']);
      expect(cm.get('p1')).toHaveLength(1);
      expect(cm.get('p1')?.[0].id).toBe('j1');
    });

    it('should build parentMap from edges (target → source nodes)', () => {
      const pm = store.parentMap();
      expect(pm.get('p1')).toHaveLength(1);
      expect(pm.get('p1')?.[0].id).toBe('a1');
      expect(pm.get('j1')).toHaveLength(1);
      expect(pm.get('j1')?.[0].id).toBe('p1');
    });
  });

  // --- selectedNode / getNode / setSelectedPaper ---

  describe('selectedNode and setSelectedPaper', () => {
    it('should return undefined when no node is selected', () => {
      expect(store.selectedNode()).toBeUndefined();
    });

    it('should return the node matching selectedNodeKey', () => {
      const p = makePaperNode('p1', 'Test');
      store.graph.set({ nodes: [p], edges: [] });
      store.selectedNodeKey.set('p1');
      expect(store.selectedNode()).toEqual(p);
    });

    it('setSelectedPaper should find paper by paper_id and set selectedNodeKey', () => {
      const p = makePaperNode('p1', 'Test');
      store.graph.set({ nodes: [p], edges: [] });
      store.setSelectedPaper('pid-p1');
      expect(store.selectedNodeKey()).toBe('p1');
    });

    it('setSelectedPaper should not change selection if paper_id not found', () => {
      store.graph.set({ nodes: [makePaperNode('p1', 'Test')], edges: [] });
      store.selectedNodeKey.set('p1');
      store.setSelectedPaper('nonexistent');
      expect(store.selectedNodeKey()).toBe('p1');
    });
  });

  // --- addNodes ---

  describe('addNodes', () => {
    it('should append nodes to the existing graph', () => {
      store.graph.set({ nodes: [makePaperNode('p1', 'First')], edges: [] });
      store.addNodes([makeAuthorNode('a1', 'Alice')]);
      expect(store.graph().nodes).toHaveLength(2);
    });
  });

  // --- addCitations / addReferences ---

  describe('addCitations', () => {
    it('should POST to citations endpoint with the paper_id', () => {
      const p = makePaperNode('p1', 'Test');
      store.graph.set({ nodes: [p], edges: [] });
      store.selectedNodeKey.set('p1');

      store.addCitations();

      const req = httpMock.expectOne((r) => r.url.includes('/papers/citations/add/'));
      expect(req.request.body).toEqual(['pid-p1']);
      req.flush({});
    });

    it('should not POST if selected node is not a Paper', () => {
      const a = makeAuthorNode('a1', 'Alice');
      store.graph.set({ nodes: [a], edges: [] });
      store.selectedNodeKey.set('a1');

      store.addCitations();

      httpMock.expectNone((r) => r.url.includes('/papers/citations/add/'));
    });

    it('should not POST if no node is selected', () => {
      store.addCitations();
      httpMock.expectNone((r) => r.url.includes('/papers/citations/add/'));
    });
  });

  describe('addReferences', () => {
    it('should POST to references endpoint with the paper_id', () => {
      const p = makePaperNode('p1', 'Test');
      store.graph.set({ nodes: [p], edges: [] });
      store.selectedNodeKey.set('p1');

      store.addReferences();

      const req = httpMock.expectOne((r) => r.url.includes('/papers/references/add/'));
      expect(req.request.body).toEqual(['pid-p1']);
      req.flush({});
    });
  });

  // --- Event-driven graph refresh ---

  describe('graph_updated event', () => {
    it('should refetch the graph when a graph_updated event is received', () => {
      const spy = jest.spyOn(toastService, 'show');

      eventsSubject.next({ type: 'graph_updated', body: {} });

      const req = httpMock.expectOne((r) => r.url.includes('/graph/get/'));
      const newGraph: KnowledgeGraph = {
        nodes: [makePaperNode('p99', 'New Paper')],
        edges: [],
      };
      req.flush(newGraph);

      expect(store.graph().nodes).toHaveLength(1);
      expect(store.graph().nodes[0].id).toBe('p99');
      expect(spy).toHaveBeenCalledWith('Graph updated!');
    });
  });

  // --- Dialog signals ---

  describe('dialog signals', () => {
    it('showAddDocuments should set showDocumentDialog to true', () => {
      store.showAddDocuments();
      expect(store.showDocumentDialog()).toBe(true);
    });

    it('bulkAddDocuments should set showDocumentDialog true and clear selectedNodeKey', () => {
      store.selectedNodeKey.set('p1');
      store.bulkAddDocuments();
      expect(store.showDocumentDialog()).toBe(true);
      expect(store.selectedNodeKey()).toBe('');
    });
  });

  // --- authorOptions ---

  describe('authorOptions', () => {
    it('should derive author options from typeMap', () => {
      store.graph.set({
        nodes: [makeAuthorNode('a1', 'Alice'), makeAuthorNode('a2', 'Bob')],
        edges: [],
      });
      const opts = store.authorOptions();
      expect(opts).toHaveLength(2);
      expect(opts[0]).toEqual({ label: 'Alice', value: 'a1' });
      expect(opts[1]).toEqual({ label: 'Bob', value: 'a2' });
    });
  });
});
