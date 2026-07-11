import { NgModule } from '@angular/core';
import { HighchartsChartModule } from 'highcharts-angular';

import { SharedModule } from '../../shared/shared.module';
import { DashboardRoutingModule } from './dashboard-routing.module';
import { DashboardComponent } from './dashboard/dashboard.component';

@NgModule({
  declarations: [DashboardComponent],
  imports: [SharedModule, HighchartsChartModule, DashboardRoutingModule],
})
export class DashboardModule {}
