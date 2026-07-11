import { Component, EventEmitter, Input, Output } from '@angular/core';
import { Client } from '../../../core/models/client.model';

@Component({
  selector: 'app-client-view-modal',
  templateUrl: './client-view-modal.component.html',
  styleUrls: ['./client-view-modal.component.scss']
})
export class ClientViewModalComponent {

  @Input() client!: Client;
  @Output() close = new EventEmitter<void>();

  get initials(): string {

    if (!this.client?.policy_holder) {
      return '';
    }

    return this.client.policy_holder
      .split(' ')
      .filter(Boolean)
      .slice(0, 2)
      .map(x => x[0].toUpperCase())
      .join('');
  }
}