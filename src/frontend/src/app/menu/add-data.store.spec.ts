import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { AddDataStore } from './add-data.store';
import { PaperRelevanceResult } from './types';

describe('AddDataStore', () => {
  let store: AddDataStore;
  let httpMock: HttpTestingController;

  const mockResults: PaperRelevanceResult[] = [
    { title: 'Graph Neural Networks', year: 2021, paperId: 'p1', authors: [{ name: 'Alice', authorId: 'a1' }] },
    { title: 'Transformers', year: 2022, paperId: 'p2', authors: [{ name: 'Bob', authorId: 'a2' }] },
  ];

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [AddDataStore],
    });

    store = TestBed.inject(AddDataStore);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  // --- Initial state ---

  it('should start with empty results and not loading', () => {
    expect(store.searchResults()).toEqual([]);
    expect(store.loading()).toBe(false);
  });

  // --- search ---

  describe('search', () => {
    it('should set loading to true while searching', () => {
      store.search('neural networks');

      expect(store.loading()).toBe(true);

      const req = httpMock.expectOne((r) => r.url.includes('/papers/search/relevance/'));
      req.flush(mockResults);
    });

    it('should fetch results and set loading to false on completion', () => {
      store.search('neural networks');

      const req = httpMock.expectOne((r) => r.url.includes('/papers/search/relevance/'));
      expect(req.request.method).toBe('GET');
      expect(req.request.url).toContain('query=neural networks');
      req.flush(mockResults);

      expect(store.searchResults()).toEqual(mockResults);
      expect(store.loading()).toBe(false);
    });

    it('should cancel previous in-flight search when a new search is triggered (switchMap)', () => {
      store.search('first query');

      const req1 = httpMock.expectOne((r) => r.url.includes('query=first query'));

      // Trigger a second search before the first completes
      store.search('second query');

      // First request should have been cancelled
      expect(req1.cancelled).toBe(true);

      const req2 = httpMock.expectOne((r) => r.url.includes('query=second query'));
      req2.flush(mockResults);

      expect(store.searchResults()).toEqual(mockResults);
    });
  });

  // --- searchPapers (direct HTTP call) ---

  describe('searchPapers', () => {
    it('should make a GET request with the search term', () => {
      store.searchPapers('transformers').subscribe((results) => {
        expect(results).toEqual(mockResults);
      });

      const req = httpMock.expectOne((r) => r.url.includes('/papers/search/relevance/?query=transformers'));
      expect(req.request.method).toBe('GET');
      req.flush(mockResults);
    });
  });

  // --- addPapersToGraph ---

  describe('addPapersToGraph', () => {
    it('should POST paper IDs to the add endpoint', () => {
      const paperIds = ['p1', 'p2', 'p3'];

      store.addPapersToGraph(paperIds).subscribe();

      const req = httpMock.expectOne((r) => r.url.includes('/papers/add/'));
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(paperIds);
      req.flush({ success: true });
    });
  });

  // --- clearResults ---

  describe('clearResults', () => {
    it('should reset searchResults to empty array', () => {
      // First populate results
      store.search('test');
      const req = httpMock.expectOne((r) => r.url.includes('/papers/search/relevance/'));
      req.flush(mockResults);
      expect(store.searchResults().length).toBe(2);

      // Then clear
      store.clearResults();
      expect(store.searchResults()).toEqual([]);
    });
  });
});
