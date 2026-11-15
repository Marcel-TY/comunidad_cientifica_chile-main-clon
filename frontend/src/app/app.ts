import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Observable } from 'rxjs';
import { ProjectCardComponent } from './project-card.component';
import { PublicationCardComponent } from './publication-card.component';
import { ResearchApiService } from './research-api.service';
import {
  ResearchProject,
  ResearchProjectInput,
  Researcher,
  ResearcherInput,
  ScientificPublication,
  ScientificPublicationInput,
} from './research.models';
import { ResearcherCardComponent } from './researcher-card.component';

@Component({
  selector: 'app-root',
  imports: [FormsModule, ProjectCardComponent, ResearcherCardComponent, PublicationCardComponent],
  templateUrl: './research-app.html',
  styleUrl: './research-app.css',
})
export class App implements OnInit {
  private readonly api = inject(ResearchApiService);

  projects: ResearchProject[] = [];
  researchers: Researcher[] = [];
  publications: ScientificPublication[] = [];
  canManage = false;
  loading = true;
  saving = false;
  errorMessage = '';
  successMessage = '';
  selectedProjectId: number | null = null;
  highlightedPublicationId: number | null = null;
  projectFormVisible = false;
  researcherFormVisible = false;
  publicationFormVisible = false;
  editingProjectId: number | null = null;
  editingResearcherId: number | null = null;
  editingPublicationId: number | null = null;

  projectDraft: ResearchProjectInput = this.emptyProject();
  researcherDraft: ResearcherInput = this.emptyResearcher();
  publicationDraft: ScientificPublicationInput = this.emptyPublication();

  ngOnInit(): void {
    this.loadPage();
  }

  get visibleResearchers(): Researcher[] {
    if (this.selectedProjectId === null) return this.researchers;
    const project = this.projects.find(({ id }) => id === this.selectedProjectId);
    if (!project) return this.researchers;
    return this.researchers.filter(({ id }) => project.researcherIds.includes(id));
  }

  selectProject(projectId: number): void {
    this.selectedProjectId = this.selectedProjectId === projectId ? null : projectId;
  }

  highlightPublication(publicationId: number): void {
    this.highlightedPublicationId = this.highlightedPublicationId === publicationId
      ? null
      : publicationId;
  }

  beginProjectCreate(): void {
    this.editingProjectId = null;
    this.projectDraft = this.emptyProject();
    this.projectFormVisible = true;
    this.successMessage = '';
  }

  editProject(project: ResearchProject): void {
    this.editingProjectId = project.id;
    this.projectDraft = {
      title: project.title,
      summary: project.summary,
      description: project.description,
      researchArea: project.researchArea,
      funder: project.funder,
      status: project.status,
      start_date: project.start_date,
      end_date: project.end_date,
      researcherIds: [...project.researcherIds],
    };
    this.projectFormVisible = true;
    this.successMessage = '';
  }

  saveProject(): void {
    const request = this.editingProjectId === null
      ? this.api.createProject(this.projectDraft)
      : this.api.updateProject(this.editingProjectId, this.projectDraft);
    this.runMutation(request, 'Proyecto guardado correctamente.', () => {
      this.projectFormVisible = false;
      this.editingProjectId = null;
      this.projectDraft = this.emptyProject();
    });
  }

  deleteProject(project: ResearchProject): void {
    if (!window.confirm(`¿Eliminar el proyecto "${project.title}"?`)) return;
    this.runMutation(
      this.api.deleteProject(project.id),
      'Proyecto eliminado.',
      () => undefined,
    );
  }

  beginResearcherCreate(): void {
    this.editingResearcherId = null;
    this.researcherDraft = this.emptyResearcher();
    this.researcherFormVisible = true;
    this.successMessage = '';
  }

  editResearcher(researcher: Researcher): void {
    this.editingResearcherId = researcher.id;
    this.researcherDraft = { ...researcher, email: '' };
    this.researcherFormVisible = true;
    this.successMessage = '';
  }

  saveResearcher(): void {
    const payload = { ...this.researcherDraft };
    if (this.editingResearcherId !== null && !payload.email) {
      delete payload.email;
    }
    const request = this.editingResearcherId === null
      ? this.api.createResearcher(payload)
      : this.api.updateResearcher(this.editingResearcherId, payload);
    this.runMutation(request, 'Investigador/a guardado/a correctamente.', () => {
      this.researcherFormVisible = false;
      this.editingResearcherId = null;
      this.researcherDraft = this.emptyResearcher();
    });
  }

  deleteResearcher(researcher: Researcher): void {
    if (!window.confirm(`¿Eliminar a "${researcher.fullName}"?`)) return;
    this.runMutation(
      this.api.deleteResearcher(researcher.id),
      'Investigador/a eliminado/a.',
      () => undefined,
    );
  }

  updateProjectResearchers(event: Event): void {
    const select = event.target as HTMLSelectElement;
    this.projectDraft.researcherIds = Array.from(select.selectedOptions)
      .map(({ value }) => Number(value));
  }

  updatePublicationResearchers(event: Event): void {
    const select = event.target as HTMLSelectElement;
    this.publicationDraft.researcherIds = Array.from(select.selectedOptions)
      .map(({ value }) => Number(value));
  }

  beginPublicationCreate(): void {
    this.editingPublicationId = null;
    this.publicationDraft = this.emptyPublication();
    this.publicationFormVisible = true;
    this.successMessage = '';
  }

  editPublication(publication: ScientificPublication): void {
    this.editingPublicationId = publication.id;
    this.publicationDraft = {
      title: publication.title,
      abstract: publication.abstract,
      journal: publication.journal,
      doi: publication.doi,
      publicationDate: publication.publicationDate,
      projectId: publication.projectId,
      researcherIds: [...publication.researcherIds],
    };
    this.publicationFormVisible = true;
    this.successMessage = '';
  }

  savePublication(): void {
    const request = this.editingPublicationId === null
      ? this.api.createPublication(this.publicationDraft)
      : this.api.updatePublication(this.editingPublicationId, this.publicationDraft);
    this.runMutation(request, 'Publicación guardada correctamente.', () => {
      this.publicationFormVisible = false;
      this.editingPublicationId = null;
      this.publicationDraft = this.emptyPublication();
    });
  }

  deletePublication(publication: ScientificPublication): void {
    if (!window.confirm(`¿Eliminar la publicación "${publication.title}"?`)) return;
    this.runMutation(
      this.api.deletePublication(publication.id),
      'Publicación eliminada.',
      () => undefined,
    );
  }

  cancelForm(form: 'project' | 'researcher' | 'publication'): void {
    if (form === 'project') {
      this.projectFormVisible = false;
      this.editingProjectId = null;
      this.projectDraft = this.emptyProject();
    } else if (form === 'researcher') {
      this.researcherFormVisible = false;
      this.editingResearcherId = null;
      this.researcherDraft = this.emptyResearcher();
    } else {
      this.publicationFormVisible = false;
      this.editingPublicationId = null;
      this.publicationDraft = this.emptyPublication();
    }
  }

  private loadPage(): void {
    this.loading = true;
    this.api.loadPage().subscribe({
      next: ({ catalog, session }) => {
        this.projects = catalog.projects;
        this.researchers = catalog.researchers;
        this.publications = catalog.publications;
        this.canManage = session.isStaff;
        this.loading = false;
        this.errorMessage = '';
      },
      error: (error: unknown) => {
        this.loading = false;
        this.errorMessage = this.describeError(error);
      },
    });
  }

  private runMutation(
    request: Observable<unknown>,
    message: string,
    onSuccess: () => void,
  ): void {
    this.saving = true;
    this.errorMessage = '';
    this.successMessage = '';
    request.subscribe({
      next: () => {
        this.saving = false;
        this.successMessage = message;
        onSuccess();
        this.loadPage();
      },
      error: (error: unknown) => {
        this.saving = false;
        this.errorMessage = this.describeError(error);
      },
    });
  }

  private describeError(error: unknown): string {
    if (error instanceof HttpErrorResponse) {
      if (error.status === 403) {
        return 'La sesión no tiene permiso para modificar estos datos o venció la protección CSRF. Inicia sesión como administrador y recarga la página.';
      }
      if (error.status === 0) {
        return 'No se pudo conectar con Django. Comprueba que el servidor esté activo y vuelve a intentar.';
      }
      const body: unknown = error.error;
      if (typeof body === 'object' && body !== null && 'detail' in body) {
        const detail = (body as { detail: unknown }).detail;
        if (typeof detail === 'string') return detail;
      }
      if (typeof body === 'object' && body !== null) {
        return Object.entries(body)
          .map(([field, messages]) => `${field}: ${Array.isArray(messages) ? messages.join(', ') : messages}`)
          .join(' ');
      }
      return `La solicitud falló (HTTP ${error.status}). Revisa los datos e inténtalo nuevamente.`;
    }
    return 'Ocurrió un error inesperado al procesar la solicitud.';
  }

  private emptyProject(): ResearchProjectInput {
    return {
      title: '',
      summary: '',
      description: '',
      researchArea: '',
      funder: '',
      status: 'proposed',
      start_date: null,
      end_date: null,
      researcherIds: [],
    };
  }

  private emptyResearcher(): ResearcherInput {
    return {
      fullName: '',
      email: '',
      institution: '',
      expertise: '',
      biography: '',
      orcid: '',
    };
  }

  private emptyPublication(): ScientificPublicationInput {
    return {
      title: '',
      abstract: '',
      journal: '',
      doi: '',
      publicationDate: '',
      projectId: null,
      researcherIds: [],
    };
  }
}
