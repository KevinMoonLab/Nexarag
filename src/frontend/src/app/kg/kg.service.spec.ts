import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { KnowledgeGraphService, KnowledgeGraphInfo, KgOperationResponse, CurrentKgInfo } from './kg.service';

describe('KnowledgeGraphService', () => {
  let service: KnowledgeGraphService;
  let httpMock: HttpTestingController;

  const mockKgList: KnowledgeGraphInfo[] = [
    { name: 'research-kg', file_path: '/data/research.db', created_at: '2024-01-15', size_mb: 12.5, description: 'Research papers' },
    { name: 'survey-kg', file_path: '/data/survey.db', created_at: '2024-02-20', size_mb: 8.3 },
  ];

  const mockOpResponse: KgOperationResponse = { message: 'Operation successful', success: true };

  const mockCurrentKg: CurrentKgInfo = {
    database: 'research-kg',
    uri: 'bolt://localhost:7687',
    status: 'connected',
  };

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [KnowledgeGraphService],
    });

    service = TestBed.inject(KnowledgeGraphService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  // --- listKnowledgeGraphs ---

  describe('listKnowledgeGraphs', () => {
    it('should GET from /kg/list/', () => {
      service.listKnowledgeGraphs().subscribe((result) => {
        expect(result).toEqual(mockKgList);
        expect(result).toHaveLength(2);
      });

      const req = httpMock.expectOne('http://localhost:8000/kg/list/');
      expect(req.request.method).toBe('GET');
      req.flush(mockKgList);
    });
  });

  // --- exportKnowledgeGraph ---

  describe('exportKnowledgeGraph', () => {
    it('should POST with name parameter', () => {
      service.exportKnowledgeGraph('my-export').subscribe((result) => {
        expect(result).toEqual(mockOpResponse);
      });

      const req = httpMock.expectOne((r) => r.url.includes('/kg/export/') && r.url.includes('name=my-export'));
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual({});
      req.flush(mockOpResponse);
    });

    it('should include description parameter when provided', () => {
      service.exportKnowledgeGraph('my-export', 'A test export').subscribe();

      const req = httpMock.expectOne(
        (r) => r.url.includes('name=my-export') && r.url.includes('description=A+test+export')
      );
      expect(req.request.method).toBe('POST');
      req.flush(mockOpResponse);
    });

    it('should omit description parameter when not provided', () => {
      service.exportKnowledgeGraph('my-export').subscribe();

      const req = httpMock.expectOne((r) => r.url.includes('/kg/export/'));
      expect(req.request.url).not.toContain('description=');
      req.flush(mockOpResponse);
    });
  });

  // --- importKnowledgeGraph ---

  describe('importKnowledgeGraph', () => {
    it('should POST with name parameter', () => {
      service.importKnowledgeGraph('research-kg').subscribe((result) => {
        expect(result).toEqual(mockOpResponse);
      });

      const req = httpMock.expectOne('http://localhost:8000/kg/import/?name=research-kg');
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual({});
      req.flush(mockOpResponse);
    });
  });

  // --- deleteKnowledgeGraph ---

  describe('deleteKnowledgeGraph', () => {
    it('should DELETE with name parameter', () => {
      service.deleteKnowledgeGraph('old-kg').subscribe((result) => {
        expect(result).toEqual(mockOpResponse);
      });

      const req = httpMock.expectOne('http://localhost:8000/kg/delete/?name=old-kg');
      expect(req.request.method).toBe('DELETE');
      req.flush(mockOpResponse);
    });
  });

  // --- getCurrentKgInfo ---

  describe('getCurrentKgInfo', () => {
    it('should GET from /kg/current/', () => {
      service.getCurrentKgInfo().subscribe((result) => {
        expect(result).toEqual(mockCurrentKg);
      });

      const req = httpMock.expectOne('http://localhost:8000/kg/current/');
      expect(req.request.method).toBe('GET');
      req.flush(mockCurrentKg);
    });
  });
});
