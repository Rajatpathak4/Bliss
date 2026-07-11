import { Component, OnInit } from '@angular/core';
import * as Highcharts from 'highcharts';

import { ApiService } from '../../../core/services/api.service';
import { API_ENDPOINTS, ApiMethod } from '../../../core/constants/api-endpoints.constant';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss'],
})
export class DashboardComponent implements OnInit {
  Highcharts: typeof Highcharts = Highcharts;
  loading = true;

  stats: any[] = [];

  revenueChart!: Highcharts.Options;
  activeUsersChart!: Highcharts.Options;
  premiumDueChart!: Highcharts.Options;
  newClientsChart!: Highcharts.Options;

  constructor(private httpService: ApiService) {}

  ngOnInit(): void {
    this.loadDashboard();
  }

  loadDashboard(): void {
    this.loading = true;
    this.httpService.requestCall(API_ENDPOINTS.GET_DASHBOARD_CHARTS, ApiMethod.GET).subscribe({
      next: (res) => {
        this.stats = res?.stats ?? [];
        this.buildCharts(res);
        this.loading = false;
      },
      error: (e) => {
        console.log('dashboard error', e);
        this.loading = false;
      },
    });
  }

  private baseAxis(categories: string[]): Partial<Highcharts.Options> {
    return {
      credits: { enabled: false },
      legend: { enabled: false },
      title: { text: undefined },
      xAxis: {
        categories,
        lineColor: '#e5e7eb',
        tickLength: 0,
        labels: { style: { color: '#94a3b8' } },
      },
      yAxis: {
        title: { text: undefined },
        gridLineColor: '#eef2f7',
        gridLineDashStyle: 'Dash',
        labels: { style: { color: '#94a3b8' } },
      },
    };
  }

  buildCharts(data: any): void {
    const months: string[] = data?.months ?? [];

    this.revenueChart = {
      ...this.baseAxis(months),
      chart: { type: 'areaspline', backgroundColor: 'transparent', height: 320 },
      colors: ['#14b8a6'],
      tooltip: { shared: true, valuePrefix: '$' },
      plotOptions: {
        areaspline: {
          lineWidth: 3,
          marker: { enabled: false },
          fillColor: {
            linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1 },
            stops: [
              [0, 'rgba(20,184,166,0.25)'],
              [1, 'rgba(20,184,166,0.0)'],
            ],
          },
        },
      },
      series: [{ type: 'areaspline', name: 'Revenue', data: data?.revenue ?? [] }],
    };

    this.activeUsersChart = {
      ...this.baseAxis(months),
      chart: { type: 'spline', backgroundColor: 'transparent', height: 320 },
      colors: ['#f59e0b'],
      tooltip: { shared: true },
      plotOptions: {
        spline: {
          lineWidth: 3,
          marker: { enabled: true, radius: 4, fillColor: '#f59e0b', lineColor: '#fff', lineWidth: 2 },
        },
      },
      series: [{ type: 'spline', name: 'Active Users', data: data?.active_users ?? [] }],
    };

    this.premiumDueChart = {
      ...this.baseAxis(months),
      chart: { type: 'column', backgroundColor: 'transparent', height: 320 },
      colors: ['#f59e0b'],
      tooltip: { shared: true },
      plotOptions: { column: { borderRadius: 4, pointWidth: 22, borderWidth: 0 } },
      series: [{ type: 'column', name: 'Overdue', data: data?.premium_due_tracker ?? [] }],
    };

    this.newClientsChart = {
      ...this.baseAxis(months),
      chart: { type: 'areaspline', backgroundColor: 'transparent', height: 320 },
      colors: ['#8b5cf6'],
      tooltip: { shared: true },
      plotOptions: {
        areaspline: {
          lineWidth: 3,
          marker: { enabled: true, radius: 4, fillColor: '#8b5cf6', lineColor: '#fff', lineWidth: 2 },
          fillColor: {
            linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1 },
            stops: [
              [0, 'rgba(139,92,246,0.22)'],
              [1, 'rgba(139,92,246,0.0)'],
            ],
          },
        },
      },
      series: [{ type: 'areaspline', name: 'New Clients', data: data?.new_clients ?? [] }],
    };
  }
}