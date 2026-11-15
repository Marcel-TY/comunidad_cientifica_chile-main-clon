import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, forkJoin } from 'rxjs';
import {
  ResearchCatalogData,
  ResearchProject,
  ResearchProjectInput,
  Researcher,
  ResearcherInput,
  ResearchSession,
  ScientificPublication,
  ScientificPublicationInput,
} from './research.models';

@Injectable({ providedIn: 'root' })
export class ResearchApiService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = '/api/research';

  loadPage(): Observable<{ catalog: ResearchCatalogData; session: ResearchSession }> {
    return forkJoin({
      catalog: this.http.get<ResearchCatalogData>(`${this.baseUrl}/`),
      session: this.http.get<ResearchSession>(`${this.baseUrl}/session/`),
    });
  }

  createProject(data: ResearchProjectInput): Observable<ResearchProject> {
    return this.http.post<ResearchProject>(`${this.baseUrl}/projects/`, data);
  }

  updateProject(id: number, data: Partial<ResearchProjectInput>): Observable<ResearchProject> {
    return this.http.patch<ResearchProject>(`${this.baseUrl}/projects/${id}/`, data);
  }

  deleteProject(id: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/projects/${id}/`);
  }

  createResearcher(data: ResearcherInput): Observable<Researcher> {
    return this.http.post<Researcher>(`${this.baseUrl}/researchers/`, data);
  }

  updateResearcher(id: number, data: Partial<ResearcherInput>): Observable<Researcher> {
    return this.http.patch<Researcher>(`${this.baseUrl}/researchers/${id}/`, data);
  }

  deleteResearcher(id: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/researchers/${id}/`);
  }

  createPublication(data: ScientificPublicationInput): Observable<ScientificPublication> {
    return this.http.post<ScientificPublication>(`${this.baseUrl}/publications/`, data);
  }

  updatePublication(
    id: number,
    data: Partial<ScientificPublicationInput>,
  ): Observable<ScientificPublication> {
    return this.http.patch<ScientificPublication>(`${this.baseUrl}/publications/${id}/`, data);
  }

  deletePublication(id: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/publications/${id}/`);
  }
}
