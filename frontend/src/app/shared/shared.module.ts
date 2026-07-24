import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

/**
 * Bundles the modules that nearly every feature needs so each feature
 * module only has to import SharedModule.
 */
@NgModule({
  declarations: [],
  imports: [CommonModule, FormsModule, ReactiveFormsModule ],
  exports: [CommonModule, FormsModule, ReactiveFormsModule ],
})
export class SharedModule {}
