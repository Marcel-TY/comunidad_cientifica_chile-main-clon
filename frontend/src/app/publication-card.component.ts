import { Component, EventEmitter, Input, Output } from '@angular/core';
import { ScientificPublication } from './research.models';

@Component({
  selector: 'app-publication-card',
  templateUrl: './publication-card.component.html',
  styleUrl: './publication-card.component.css',
})
export class PublicationCardComponent {
  @Input({ required: true }) publication!: ScientificPublication;
  @Input() highlighted = false;
  @Output() publicationHighlighted = new EventEmitter<number>();

  toggleHighlight(): void {
    this.publicationHighlighted.emit(this.publication.id);
  }
}
