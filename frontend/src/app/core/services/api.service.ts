import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { catchError, Observable, throwError } from 'rxjs';

import { environment } from '../../../environments/environment';
import { ApiMethod } from '../constants/api-endpoints.constant';
import { GlobalServiceService } from './global-service.service';

/**
 * Thin wrapper over HttpClient that prefixes every call with
 * environment.apiBaseUrl. The AuthInterceptor adds the Bearer token,
 * so services here stay tiny and readable.
 */
@Injectable({ providedIn: 'root' })
export class ApiService {
  constructor(private http: HttpClient, private gbServices: GlobalServiceService) {}

requestCall(
  api: any,
  method: ApiMethod,
  data?: any,
): Observable<any> {

  let BaseUrl = environment.apiBaseUrl;

  // if (this.gbServices.logindata && !fastApiCalling) {
  //   BaseUrl = environment.apiBaseUrl;
  // }

  data = data ?? "";

  let response: Observable<any>;

  if (!api) {
    throw new Error('API endpoint is required.');
  }

  switch (method) {
    case ApiMethod.GET:
      response = this.http
        .get(BaseUrl + api + data)
        .pipe(catchError(error => this.handleError(error)));
      break;

    case ApiMethod.POST:
      response = this.http
        .post(BaseUrl + api, data)
        .pipe(catchError(error => this.handleError(error)));
      break;

    case ApiMethod.PUT:
      response = this.http
        .put(BaseUrl + api, data)
        .pipe(catchError(error => this.handleError(error)));
      break;

    case ApiMethod.DELETE:
      response = this.http
        .delete(BaseUrl + api)
        .pipe(catchError(error => this.handleError(error)));
      break;

    default:
      throw new Error('Unsupported API method');
  }

  return response;
}

 handleError(error: any) {
    if (error.error?.message && error.status !== 404 && error.status !== 403) {
      this.gbServices.showToastr(error.error.message, 'error');
      // this.toast.error(error.error.message);
    }
    if (error.error?.detail && error?.status === 400) {
      this.gbServices.showToastr(error.error?.detail, 'error');
      // this.toast.error(error.error.detail);
    }
    return throwError(() => error);
  }

  displayHeader(uid: any) {
    localStorage.setItem("showHeader" + uid, "Y");
  }
  hideHeader(uid: any) {
    localStorage.removeItem("showHeader" + uid);
  }


  requestHealthCheck(api: string, data?: any): Observable<any> {
    const BaseUrl = environment.apiBaseUrl;
    const url = BaseUrl + api;
    let response: Observable<any>;
    response = this.http.post(url, data).pipe(catchError(error => this.handleError(error)));
    return response;
  }


  downloadfile(api: any, method: ApiMethod, data?: any, apitype?: boolean): Observable<any> {
    let BaseUrl = "";

    BaseUrl = environment.apiBaseUrl;

    const httpOptions = {
      responseType: "blob" as "json",
    };

    let getparam: any;

    if (data !== undefined) {
      getparam = "/" + data;
    } else {
      getparam = "";
    }

    let response: Observable<any>;

    switch (method) {
      case ApiMethod.GET:
        response = this.http.get(BaseUrl + api + getparam, httpOptions);
        break;
      case ApiMethod.POST:
        response = this.http.post(BaseUrl + api, data, httpOptions);
        break;
      default:
        break;
    }

     return new Observable((observer) => {
    response?.subscribe({
      next: (res: any) => {
        const blob = new Blob([res]);
        if (blob.type === 'application/json' || blob.size < 200) {
          const reader = new FileReader();
          reader.onload = () => {
            try {
              const json = JSON.parse(reader.result as string);
              const message = json?.message || json?.detail || 'Something went wrong';
              this.gbServices.showToastr(message, 'error');
            } catch {
              this.gbServices.showToastr('Invalid error response', 'error');
            }
            observer.next(null);
            observer.complete();
          };
          reader.readAsText(blob);
        } else {
          observer.next(blob);
          observer.complete();
        }
      },
      error: (err) => {
        this.gbServices.showToastr('Download failed', 'error');
        observer.error(err);
      }
    })
  })
}
}
