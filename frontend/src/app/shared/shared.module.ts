import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { LoaderComponent } from '../features/loader/loader/loader.component';

/**
 * Bundles the modules that nearly every feature needs so each feature
 * module only has to import SharedModule.
 */
@NgModule({
  declarations: [LoaderComponent],
  imports: [CommonModule, FormsModule, ReactiveFormsModule ],
  exports: [CommonModule, FormsModule, ReactiveFormsModule,LoaderComponent ],
})
export class SharedModule {}
