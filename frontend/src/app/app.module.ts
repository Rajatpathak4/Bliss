import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HTTP_INTERCEPTORS, provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { LayoutModule } from './layout/layout.module';
import { AuthInterceptor } from './core/interceptors/auth.interceptor';
import { SharedModule } from './shared/shared.module'; 

@NgModule({
  declarations: [AppComponent],
  imports: [BrowserModule, AppRoutingModule],
  providers: [
  provideHttpClient(withInterceptorsFromDi()),
  { provide: HTTP_INTERCEPTORS, useClass: AuthInterceptor, multi: true },
],
  bootstrap: [AppComponent],
})
export class AppModule {}
