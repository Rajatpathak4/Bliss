import { NgModule } from '@angular/core';
import { RouterModule } from '@angular/router';

import { SharedModule } from '../shared/shared.module';
import { NavbarComponent } from './navbar/navbar.component';
import { MainLayoutComponent } from './main-layout/main-layout.component';

/**
 * The app shell. NavbarComponent is exported so the (public) forgot-password
 * page can reuse it; MainLayoutComponent is exported for the root routing.
 */
@NgModule({
  declarations: [NavbarComponent, MainLayoutComponent],
  imports: [SharedModule, RouterModule],
  exports: [NavbarComponent, MainLayoutComponent],
})
export class LayoutModule {}
