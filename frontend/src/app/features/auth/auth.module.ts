import { NgModule } from '@angular/core';

import { SharedModule } from '../../shared/shared.module';
import { AuthRoutingModule } from './auth-routing.module';
import { AuthLayoutComponent } from './auth-layout/auth-layout.component';
import { LoginComponent } from './login/login.component';
import { SignupComponent } from './signup/signup.component';

@NgModule({
  declarations: [AuthLayoutComponent, LoginComponent, SignupComponent],
  imports: [SharedModule, AuthRoutingModule],
})
export class AuthModule {}
