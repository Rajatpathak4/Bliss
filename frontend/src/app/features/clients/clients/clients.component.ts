import { Component, OnInit } from '@angular/core';

import { Client, NewClient } from '../../../core/models/client.model';
import { API_ENDPOINTS, ApiMethod } from '../../../core/constants/api-endpoints.constant';
import { ApiService } from '../../../core/services/api.service';
import { environment } from '../../../../environments/environment';
import { GlobalServiceService } from '../../../core/services/global-service.service';
type PanelMode = 'none' | 'upload' | 'add';

@Component({
  selector: 'app-clients',
  templateUrl: './clients.component.html',
  styleUrls: ['./clients.component.scss'],
})
export class ClientsComponent implements OnInit {
  mode: PanelMode = 'upload';

  // clients : any;
  // clientRecord: any;
  // modalData: any;
clients: Client[] = [];
filtered: Client[] = [];

clientRecord = 0;

viewClient: Client | null = null;
editClient: Client | null = null;



  searchTerm = '';
  loading = true;

  // Upload panel state
  dragging = false;
  selectedFile: File | null = null;
  uploadMessage = '';


  constructor( private api: ApiService,private  glbSrvc: GlobalServiceService) {}

  ngOnInit(): void {
    this.getClients();
    
  }


getClients(): void {

  this.api.requestCall(
    API_ENDPOINTS.GET_USER_TABLE_DATA,
    ApiMethod.GET
  ).subscribe({
    next: (res: any) => {
      this.clients = res.value ?? [];
      this.applyFilter();
      
    },

    error: err => this.glbSrvc.showToastr('Something went wrong', 'error')

  });

}

getClientModalData(id: number): void {

  const url =
    `${API_ENDPOINTS.USER_MODAL_DATA}?user_id=${id}`;

  this.api.requestCall(url, ApiMethod.GET)
    .subscribe({
      next: (res: any) => {
        this.viewClient = res;
        
      },
      error: err => console.error(err)

    });

}
    
onDelete(client: Client): void {
  let url = `${API_ENDPOINTS.DELETE_USER_DATA}?policy_number=${client.policy_number}`
  this.api.requestCall(url,ApiMethod.GET)
  .subscribe({
    next: () =>{  this.getClients(),
    this.glbSrvc.showToastr("Record Deleted Successfully", 'success')} ,
    error: err => console.error(err)

  });

}

onClientAdded(payload: any): void {
  this.api
    .requestCall(API_ENDPOINTS.ADD_USER_DATA, ApiMethod.POST, payload)
    .subscribe({
      next: () => {
        this.mode = 'none';
        this.getClients();
         this.glbSrvc.showToastr('Data Added Successfully', 'success')
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
        this.glbSrvc.showToastr('Data Updarted Successfully', 'success')
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
    .slice(0,2)
    .map(x => x[0].toUpperCase())
    .join("");

}

  trackById(_i: number, c: Client): number {
    return c.id;
  }

    // -------------- new code ------------------------

























  /* ---------- Panel toggling ---------- */
  setMode(mode: PanelMode): void {
    this.mode = this.mode === mode ? 'none' : mode;
  }

  /* ---------- Search ---------- */
  onSearch(term: string): void {
    this.searchTerm = term;
    this.applyFilter();
  }

private applyFilter(): void {

  const q = this.searchTerm.trim().toLowerCase();

  this.filtered = !q
    ? [...this.clients]
    : this.clients.filter(c =>
        [
          c.policy_holder,
          c.email,
          c.phone_number,
          c.policy_number,
          c.mode
        ]
          .filter(Boolean)
          .some(v => String(v).toLowerCase().includes(q))
      );

  this.clientRecord = this.filtered.length;

}

  /* ---------- Add client ---------- */

openEdit(client: any): void {
  const url = `${API_ENDPOINTS.USER_MODAL_DATA}?user_id=${client.id}`;
  this.api.requestCall(url, ApiMethod.GET).subscribe({
    next: (res: any) => {
      this.editClient = res;
    },

  });

}


  /* ---------- Upload panel ---------- */
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

downloadTemplate(){}



}
