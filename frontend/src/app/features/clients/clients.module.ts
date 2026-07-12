import { NgModule } from '@angular/core';

import { SharedModule } from '../../shared/shared.module';
import { ClientsRoutingModule } from './clients-routing.module';
import { ClientsComponent } from './clients/clients.component';
import { ClientFormComponent } from './client-form/client-form.component';
import { ClientViewModalComponent } from './client-view-modal/client-view-modal.component';
import { ClientEditModalComponent } from './client-edit-modal/client-edit-modal.component';
import { NgxPaginationModule } from 'ngx-pagination';

@NgModule({
  declarations: [
    ClientsComponent,
    ClientFormComponent,
    ClientViewModalComponent,
    ClientEditModalComponent,
  ],
  imports: [SharedModule, ClientsRoutingModule, NgxPaginationModule],
})
export class ClientsModule {}
