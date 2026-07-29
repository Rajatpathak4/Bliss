import { Component, EventEmitter, inject, Input, Output, OnChanges, SimpleChanges } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { Client } from '../../../core/models/client.model';

@Component({
  selector: 'app-client-edit-modal',
  templateUrl: './client-edit-modal.component.html',
  styleUrls: ['./client-edit-modal.component.scss'],
})
export class ClientEditModalComponent implements OnChanges {
  private fb = inject(FormBuilder);

  @Input() client!: Client;

  @Output() save = new EventEmitter<Client>();
  @Output() close = new EventEmitter<void>();

  form = this.fb.group({
    family_code: [''],
    agent_code : [''],
    policy_holder: ['', Validators.required],
    policy_number: [''],
    dob: [''],
    phone_number: [''],
    email: ['', Validators.email],
    address: [''],
    agency_code: [''],
    commecement_date: [''],
    plan: [0],
    term: [0],
    ppt: [0],
    sum_assured: [0],
    mode: [''],
    fup_date: [''],
    premium: [0],
    nominee: ['']
  });

  ngOnChanges(changes: SimpleChanges): void {

    if (changes['client'] && this.client) {

      this.form.patchValue({
        agency_code: this.client.agency_code,
        agent_code: this.client.agent_code,
        family_code: this.client.family_code,
        policy_holder: this.client.policy_holder,
        policy_number: this.client.policy_number,
        dob: this.client.dob,
        phone_number: this.client.phone_number,
        email: this.client.email,
        address: this.client.address,
        commecement_date: this.client.commecement_date,
        plan: this.client.plan,
        term: this.client.term,
        ppt: this.client.ppt,
        sum_assured: this.client.sum_assured,
        mode: this.client.mode,
        fup_date: this.client.fup_date,
        premium: this.client.premium,
        nominee: this.client.nominee

      });
    }
  }

  get f() {
    return this.form.controls;
  }

submit() {

    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    this.save.emit({
      ...this.client,
      ...this.form.getRawValue()
    } as Client);
  }

}
