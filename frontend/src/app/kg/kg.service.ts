import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface KnowledgeGraphInfo {
  name: string;
  file_path: string;
  created_at: string;
  size_mb: number;
  description?: string;
}

export interface KgOperationResponse {
  message: string;
  success: boolean;
}

export interface CurrentKgInfo {
  database: string;
  uri: string;
  status: string;
  message?: string;
}

@Injectable({
  providedIn: 'root'
})
export class KnowledgeGraphService {
  private baseUrl = 'http://localhost:8000/kg';

  constructor(private http: HttpClient) {}

  listKnowledgeGraphs(): Observable<KnowledgeGraphInfo[]> {
    return this.http.get<KnowledgeGraphInfo[]>(`${this.baseUrl}/list/`);
  }

  exportKnowledgeGraph(name: string, description?: string): Observable<KgOperationResponse> {
    const params = new URLSearchParams();
    params.append('name', name);
    if (description) {
      params.append('description', description);
    }
    
    return this.http.post<KgOperationResponse>(`${this.baseUrl}/export/?${params.toString()}`, {});
  }

  importKnowledgeGraph(name: string): Observable<KgOperationResponse> {
    return this.http.post<KgOperationResponse>(`${this.baseUrl}/import/?name=${name}`, {});
  }

  deleteKnowledgeGraph(name: string): Observable<KgOperationResponse> {
    return this.http.delete<KgOperationResponse>(`${this.baseUrl}/delete/?name=${name}`);
  }

  getCurrentKgInfo(): Observable<CurrentKgInfo> {
    return this.http.get<CurrentKgInfo>(`${this.baseUrl}/current/`);
  }
}
