import { Component, EventEmitter, Input, Output } from '@angular/core';
import { ResearchProject } from './research.models';

@Component({
  selector: 'app-project-card',
  templateUrl: './project-card.component.html',
  styleUrl: './project-card.component.css',
})
export class ProjectCardComponent {
  @Input({ required: true }) project!: ResearchProject;
  @Input() selected = false;
  @Output() projectSelected = new EventEmitter<number>();

  selectProject(): void {
    this.projectSelected.emit(this.project.id);
  }
}
