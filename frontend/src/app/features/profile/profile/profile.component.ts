import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';

import { ApiService } from '../../../core/services/api.service';
import { API_ENDPOINTS, ApiMethod } from '../../../core/constants/api-endpoints.constant';
import { AuthUser } from '../../../core/models/user.model';
import { GlobalServiceService } from '../../../core/services/global-service.service';

@Component({
  selector: 'app-profile',
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.scss'],
})
export class ProfileComponent implements OnInit {
  user: AuthUser | null = null;
  editMode = false;
  saving = false;
  uploading = false;

  form!: FormGroup;
  previewUrl: string | null = null;
  selectedFile: File | null = null;

  constructor(
    private api: ApiService,
    private glbSrvc: GlobalServiceService,
    private fb: FormBuilder,
  ) {}

  ngOnInit(): void {
    this.loadProfile();
  }

  get f() {
    return this.form.controls;
  }

loadProfile(): void {
  this.api.requestCall(API_ENDPOINTS.GET_PROFILE, ApiMethod.GET).subscribe({
    next: (res) => {
      this.user = res?.value ?? res;   // 'data' ko 'value' se badla
      this.buildForm();
    },
    error: (err) => {
      console.error(err);
      this.glbSrvc.showToastr('Failed to load profile', 'error');
    },
  });
}

  private buildForm(): void {
    this.form = this.fb.group({
      name: [this.user?.fullName, Validators.required],
      email: [this.user?.email, [Validators.required, Validators.email]],
      phone_number: [this.user?.phone_number],
      company: [this.user?.company],
      location: [this.user?.location],
    });
  }

  toggleEdit(): void {
    this.editMode = !this.editMode;
    if (!this.editMode) {
      this.buildForm();
      this.previewUrl = null;
      this.selectedFile = null;
    }
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;

    if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
      this.glbSrvc.showToastr('Only JPG, PNG, or WEBP images allowed', 'error');
      return;
    }
    if (file.size > 2 * 1024 * 1024) {
      this.glbSrvc.showToastr('Image must be under 2MB', 'error');
      return;
    }

    this.selectedFile = file;
    const reader = new FileReader();
    reader.onload = () => (this.previewUrl = reader.result as string);
    reader.readAsDataURL(file);
  }

  save(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    this.saving = true;

    this.api.requestCall(API_ENDPOINTS.UPDATE_PROFILE, ApiMethod.PUT, this.form.value).subscribe({
      next: () => {
        if (this.selectedFile) {
          this.uploadAvatar();
        } else {
          this.finishSave();
        }
      },
      error: (err) => {
        this.saving = false;
        console.error(err);
        this.glbSrvc.showToastr('Failed to update profile', 'error');
      },
    });
  }

  private uploadAvatar(): void {
    const formData = new FormData();
    formData.append('file', this.selectedFile as File);
    this.uploading = true;

    this.api.requestCall(API_ENDPOINTS.UPLOAD_PROFILE_IMAGE, ApiMethod.POST, formData).subscribe({
      next: () => {
        this.uploading = false;
        this.finishSave();
      },
      error: (err) => {
        this.uploading = false;
        this.saving = false;
        console.error(err);
        this.glbSrvc.showToastr('Profile saved, but image upload failed', 'error');
      },
    });
  }

  private finishSave(): void {
    this.saving = false;
    this.editMode = false;
    this.selectedFile = null;
    this.previewUrl = null;
    this.glbSrvc.showToastr('Profile updated successfully', 'success');
    this.loadProfile();
  }
}