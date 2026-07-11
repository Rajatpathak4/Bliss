import { Injectable } from '@angular/core';
import { Observable, forkJoin, of } from 'rxjs';
import { catchError, map } from 'rxjs/operators';

import { ApiService } from './api.service';
import { API_ENDPOINTS, ApiMethod } from '../constants/api-endpoints.constant';
import { SeriesData, StatCard } from '../models/dashboard.model';

/**
 * Shapes the two dashboard endpoints are expected to return. Every field is
 * optional so a partial/renamed backend response degrades gracefully.
 *
 *  GET /get_active_client -> { count, label?, hint?, trend?, categories?, series?, target? }
 *  GET /get_premium_stats -> { count, label?, hint?, trend?, categories?, series? }
 */
interface ActiveClientResponse {
  count?: number;
  label?: string;
  hint?: string;
  trend?: 'up' | 'flat';
  categories?: string[];
  series?: number[];
  target?: number[];
}
interface PremiumStatsResponse {
  count?: number;
  label?: string;
  hint?: string;
  trend?: 'up' | 'flat';
  categories?: string[];
  series?: number[];
}

@Injectable({ providedIn: 'root' })
export class DashboardService {
  activeClient: any;
  premiumStats: any;
  constructor(private http: ApiService) {}

private activeClient$(): Observable<ActiveClientResponse> {
  return this.http
    .requestCall(API_ENDPOINTS.GET_ACTIVE_CLIENT, ApiMethod.GET)
    .pipe(
      catchError((error) => {
        console.error('Error fetching active client data:', error);
        return of({});
      })
    );
}

private premiumStats$(): Observable<PremiumStatsResponse> {
  return this.http
    .requestCall(API_ENDPOINTS.GET_PREMIUM_STATS, ApiMethod.GET)
    .pipe(
      catchError((error) => {
        console.error('Error fetching premium stats data:', error);
        return of({});
      })
    );
}


getStatCards(){
  // return forkJoin({
  //   active: this.activeClient$(),
  //   premium: this.premiumStats$(),
  // }).pipe(
  //   map(({ active, premium }) => {
  //     const cards = STAT_CARDS.map((c) => ({ ...c }));

  //     const activeCard = cards.find((c) => c.key === 'active-users');
  //     if (activeCard) {
  //       if (active.label) activeCard.value = active.label;
  //       else if (active.count != null) activeCard.value = `${active.count} clients`;
  //       if (active.hint) activeCard.hint = active.hint;
  //       if (active.trend) activeCard.trend = active.trend;
  //     }

  //     const premiumCard = cards.find((c) => c.key === 'premium-due');
  //     if (premiumCard) {
  //       if (premium.label) premiumCard.value = premium.label;
  //       else if (premium.count != null) premiumCard.value = `${premium.count} renewals`;
  //       if (premium.hint) premiumCard.hint = premium.hint;
  //       if (premium.trend) premiumCard.trend = premium.trend;
  //     }

  //     return cards;
  //   })
  // );
}

getSeries() {
//   return forkJoin({
//     active: this.activeClient$(),
//     premium: this.premiumStats$(),
//   }).pipe(
//     map(({ active, premium }) => {
//       const base: SeriesData = { ...CHART_SERIES };
//       const categories =
//         active.categories ?? premium.categories ?? base.categories;

//       return {
//         ...base,
//         categories,
//         activeUsers: active.series ?? base.activeUsers,
//         activeUsersTarget: active.target ?? base.activeUsersTarget,
//         premiumDue: premium.series ?? base.premiumDue,
//       };
//     })
//   );
// }
}
}