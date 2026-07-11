import { NgModule } from '@angular/core';

import { SharedModule } from '../../shared/shared.module';
import { LayoutModule } from '../../layout/layout.module';
import { ForgotPasswordRoutingModule } from './forgot-password-routing.module';
import { ForgotPasswordComponent } from './forgot-password/forgot-password.component';

@NgModule({
  declarations: [ForgotPasswordComponent],
  imports: [SharedModule, LayoutModule, ForgotPasswordRoutingModule],
})
export class ForgotPasswordModule {}
