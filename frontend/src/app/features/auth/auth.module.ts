import { NgModule } from "@angular/core";

import { SharedModule } from "../../shared/shared.module";
import { AuthRoutingModule } from "./auth-routing.module";
import { AuthLayoutComponent } from "./auth-layout/auth-layout.component";
import { LoginComponent } from "./login/login.component";
import { SignupComponent } from "./signup/signup.component";
import { GoogleSigninButtonDirective } from "@abacritt/angularx-social-login";

@NgModule({
  declarations: [AuthLayoutComponent, LoginComponent, SignupComponent],
  imports: [SharedModule, AuthRoutingModule, GoogleSigninButtonDirective],
})
export class AuthModule {}