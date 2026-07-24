import { Component, OnInit, OnDestroy } from '@angular/core';

import { Client, NewClient } from '../../../core/models/client.model';
import { API_ENDPOINTS, ApiMethod } from '../../../core/constants/api-endpoints.constant';
import { ApiService } from '../../../core/services/api.service';
import { environment } from '../../../../environments/environment';
import { GlobalServiceService } from '../../../core/services/global-service.service';
import { debounceTime, distinctUntilChanged } from 'rxjs/operators';
import { Subject } from 'rxjs';
import Swal from 'sweetalert2';

type PanelMode = 'none' | 'upload' | 'add';

@Component({
  selector: 'app-clients',
  templateUrl: './clients.component.html',
  styleUrls: ['./clients.component.scss'],
})
export class ClientsComponent implements OnInit, OnDestroy {
  mode: PanelMode = 'upload';
  clients: Client[] = [];
  clientRecord = 0;
  viewClient: Client | null = null;
  editClient: Client | null = null;
  searchTerm = '';
  searchInput = '';
  loading = true;
  dragging = false;
  selectedFile: File | null = null;
  uploadMessage = '';

  currentPage = 1;
  pageSize = 10;

  pagination = {
    total_records: 0,
    total_pages: 0,
    current_page: 1,
    items_per_page: 10
  };

  private searchSubject = new Subject<string>();

  constructor(private api: ApiService, private glbSrvc: GlobalServiceService) {
    this.searchSubject
      .pipe(
        debounceTime(300),
        distinctUntilChanged()
      )
      .subscribe((term) => {
        this.searchTerm = term;
        this.currentPage = 1;
        this.getClients();
      });
  }

  ngOnInit(): void {
    this.getClients();
  }

  ngOnDestroy(): void {
    this.searchSubject.complete();
  }

  getClients(): void {
    const searchParam = this.searchTerm ? `&search=${encodeURIComponent(this.searchTerm)}` : '';

    this.api.requestCall(
      `${API_ENDPOINTS.GET_USER_TABLE_DATA}?page_no=${this.currentPage}&limit=${this.pageSize}${searchParam}`,
      ApiMethod.GET
    ).subscribe({
      next: (res: any) => {
        this.clients = res.value.table_data;
        this.pagination = res.value.pagination;
        this.clientRecord = this.pagination.total_records;
      },
      error: () => {
        this.glbSrvc.showToastr('Something went wrong', 'error');
      }
    });
  }

  onPageChange(page: number): void {
    this.currentPage = page;
    this.getClients();
  }

  onPageSizeChange(): void {
    this.currentPage = 1;
    this.getClients();
  }

  onSearch(term: string): void {
    this.searchInput = term;
    this.searchSubject.next(term);
  }

  getClientModalData(id: number): void {
    const url = `${API_ENDPOINTS.USER_MODAL_DATA}?user_id=${id}`;
    this.api.requestCall(url, ApiMethod.GET)
      .subscribe({
        next: (res: any) => {
          this.viewClient = res;
        },
        error: err => console.error(err)
      });
  }

onDelete(client: Client): void {
  const url = `${API_ENDPOINTS.DELETE_USER_DATA}?policy_number=${client.policy_number}`;

  Swal.fire({
    title: "Warning!",
    text: "Are you sure you want to delete this record? All the related columns will be deleted.",
    icon: "warning",
    confirmButtonText: "Yes, Delete it!",
    cancelButtonText: "No, Keep it!",
    showCancelButton: true,
    iconColor: '#fb8c00',
    focusConfirm: false,
    customClass: {
      popup: 'bg-dark',
      title: 'text-light',
      confirmButton: 'bg-success border-0',
      cancelButton: 'bg-danger ms-3',
      htmlContainer: 'text-light'
    }
  }).then((result) => {
    if (!result.isConfirmed) {
      return;
    }

    this.api.requestCall(url, ApiMethod.GET).subscribe({
      next: () => {
        this.getClients();
        this.glbSrvc.showToastr("Record Deleted Successfully", 'success');
      },
      error: (err) => {
        console.error(err);
        this.glbSrvc.showToastr("Failed to delete record. Please try again.", 'error');
      }
    });
  });
}

  onClientAdded(payload: any): void {
    this.api
      .requestCall(API_ENDPOINTS.ADD_USER_DATA, ApiMethod.POST, payload)
      .subscribe({
        next: () => {
          this.mode = 'none';
          this.getClients();
          this.glbSrvc.showToastr('Data Added Successfully', 'success');
        },
        error: (err) => console.error(err)
      });
  }

  onSaved(client: any): void {
    this.api
      .requestCall(API_ENDPOINTS.UPDATE_USER_DATA, ApiMethod.POST, client)
      .subscribe({
        next: () => {
          this.editClient = null;
          this.glbSrvc.showToastr('Data Updated Successfully', 'success');
          this.getClients();
        },
        error: (err) => console.error(err)
      });
  }

  submitUpload(): void {
    if (!this.selectedFile) {
      return;
    }

    const form = new FormData();
    form.append("files", this.selectedFile);

    this.api.requestCall(
      API_ENDPOINTS.UPLOAD_USER_EXCEL,
      ApiMethod.POST,
      form
    )
    .subscribe({
      next: (res: any) => {
        this.uploadMessage = res.message;
        this.selectedFile = null;
        this.getClients();
      },
      error: err => console.error(err)
    });
  }

  initials(name: string): string {
    return name
      .split(" ")
      .filter(Boolean)
      .slice(0, 2)
      .map(x => x[0].toUpperCase())
      .join("");
  }

  trackById(_i: number, c: Client): number {
    return c.id;
  }

  setMode(mode: PanelMode): void {
    this.mode = this.mode === mode ? 'none' : mode;
  }

  openEdit(client: any): void {
    const url = `${API_ENDPOINTS.USER_MODAL_DATA}?user_id=${client.id}`;
    this.api.requestCall(url, ApiMethod.GET).subscribe({
      next: (res: any) => {
        this.editClient = res;
      },
    });
  }

  onDragOver(event: DragEvent): void {
    event.preventDefault();
    this.dragging = true;
  }
  onDragLeave(event: DragEvent): void {
    event.preventDefault();
    this.dragging = false;
  }
  onDrop(event: DragEvent): void {
    event.preventDefault();
    this.dragging = false;
    const file = event.dataTransfer?.files?.[0];
    if (file) this.selectedFile = file;
  }
  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files?.length) this.selectedFile = input.files[0];
  }

downloadTemplate() {
  const link = document.createElement('a');
  link.href = 'assets/Template.xlsx';
  link.download = 'Template.xlsx';  
  link.click();
}
}