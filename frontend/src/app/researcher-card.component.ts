import { Component, Input } from '@angular/core';
import { Researcher } from './research.models';

@Component({
  selector: 'app-researcher-card',
  templateUrl: './researcher-card.component.html',
  styleUrl: './researcher-card.component.css',
})
export class ResearcherCardComponent {
  @Input({ required: true }) researcher!: Researcher;
}
