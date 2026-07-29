import { Component, EventEmitter, inject, Output } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';

import { NewClient } from '../../../core/models/client.model';

@Component({
  selector: 'app-client-form',
  templateUrl: './client-form.component.html',
  styleUrls: ['./client-form.component.scss']
})
export class ClientFormComponent {
  private fb = inject(FormBuilder);

  @Output() added = new EventEmitter<NewClient>();

  form = this.fb.group({

    policy_holder: ['', Validators.required],
    agent_code :[''], 
    from_date : [''],
    to_date : [''],
    email: ['', Validators.email],
    phone_number: [''],
    address: [''],
    dob: [''],
    family_code: [''],
    policy_number: [''],
    agency_code: [''],
    commecement_date: [''],
    mode: [''],
    plan: [0],
    term: [0],
    ppt: [0],
    sum_assured: [0],
    premium: [0],
    fup_date: [''],
    nominee: ['']

  });

  get f() {
    return this.form.controls;
  }

submit(): void {
  if (this.form.invalid) {
    this.form.markAllAsTouched();
    return;
  }

  const value = this.form.getRawValue();

  const payload: NewClient = {
    agent_code: value.agent_code!,
    policy_holder: value.policy_holder!,
    from_date: value.from_date!,
    to_date: value.to_date!,
    email: value.email!,
    phone_number: value.phone_number!,
    address: value.address!,
    dob: value.dob!,
    family_code: value.family_code!,
    policy_number: value.policy_number!,
    agency_code: value.agency_code!,
    commecement_date: value.commecement_date!,
    plan: value.plan!,
    term: Number(value.term),
    ppt: Number(value.ppt),
    sum_assured: Number(value.sum_assured),
    mode: value.mode!,
    fup_date: value.fup_date!,
    premium: Number(value.premium),
    nominee: value.nominee!
  };

  this.added.emit(payload);
}

  reset(): void {

    this.form.reset({
    policy_holder:'',
    email: null,
    phone_number: null,
    address: '',
    dob: null,
    family_code:null,
    policy_number: null,
    agency_code:null,
    commecement_date: null,
    mode: null,
    fup_date: null,
    nominee : '',
    plan: null,
    term: null,
    ppt: null,
    premium: null,
    sum_assured: null,
    agent_code: null

    });

  }

}
