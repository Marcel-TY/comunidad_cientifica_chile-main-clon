import { Component } from '@angular/core';
import { ResearchProject, Researcher, ScientificPublication } from './research.models';
import { ProjectCardComponent } from './project-card.component';
import { ResearcherCardComponent } from './researcher-card.component';
import { PublicationCardComponent } from './publication-card.component';

@Component({
  selector: 'app-root',
  imports: [ProjectCardComponent, ResearcherCardComponent, PublicationCardComponent],
  templateUrl: './research-app.html',
  styleUrl: './research-app.css'
})
export class App {
  private readonly data = this.readResearchData();
  readonly projects = this.data.projects;
  readonly researchers = this.data.researchers;
  readonly publications = this.data.publications;
  selectedProjectId: number | null = null;
  highlightedPublicationId: number | null = null;

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

  private readResearchData(): {
    projects: ResearchProject[];
    researchers: Researcher[];
    publications: ScientificPublication[];
  } {
    const element = document.getElementById('research-data');
    if (!element?.textContent) {
      throw new Error('No se encontró el conjunto de datos científicos renderizado por Django.');
    }
    return JSON.parse(element.textContent);
  }
}
