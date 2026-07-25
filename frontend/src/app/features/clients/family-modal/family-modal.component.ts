import { Component, EventEmitter, Input, Output } from '@angular/core';

@Component({
  selector: 'app-family-modal',
  templateUrl: './family-modal.component.html',
  styleUrls: ['./family-modal.component.scss'],
})
export class FamilyModalComponent {
  @Input() family: any;
  @Output() close = new EventEmitter<void>();

  initials(name: string): string {
    if (!name) return '';
    return name
      .split(' ')
      .filter(Boolean)
      .slice(0, 2)
      .map((x) => x[0].toUpperCase())
      .join('');
  }
}