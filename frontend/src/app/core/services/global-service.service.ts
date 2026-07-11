import { Injectable } from "@angular/core";
import { BehaviorSubject } from "rxjs";
import { DatePipe } from "@angular/common";
import Swal, { SweetAlertIcon, SweetAlertOptions, SweetAlertResult } from 'sweetalert2'

declare const window: any;

@Injectable({
  providedIn: "root",
})
export class GlobalServiceService {
  public ProfilePicUpdate = new BehaviorSubject("");
  private idSource = new BehaviorSubject<number>(0);
  currentId = this.idSource.asObservable();
  private outageSource = new BehaviorSubject<any>("");
  outageItem = this.outageSource.asObservable();
  menuTitle = '';
  profilepic = '';
  logindata = null;
  sidebarMenu = [];
  constructor( ) {
    window.angularComponent = this;
  }
  goToTop() {
    window.scroll({
      top: 0,
      left: 0,
      behavior: "smooth",
    });
  }

  //SWEETALERT AS A TOASTR....
  showToastr(message: string, type: SweetAlertIcon): void {
    const Toast: SweetAlertOptions = {
      toast: true,
      position: 'top-end',
      showConfirmButton: false,
      timer: 5000,
      timerProgressBar: true,
      icon: type,
      title: message
    };

    Swal.fire(Toast);
  }


  punchingId(id: number) {
    this.idSource.next(id);
  }

  outageContent(item: any) {
    this.outageSource.next(item);
  }

  triggerSweetAlert(alertOptions: SweetAlertOptions): Promise<SweetAlertResult<any>> {
    alertOptions.customClass = {
      popup: 'bg-dark',
      title: 'text-light',
      confirmButton: 'bg-success border-0',
      cancelButton: 'bg-danger ms-3',
      htmlContainer: 'text-light'
    }
    alertOptions.showCancelButton = alertOptions.showCancelButton === false ? false : true;
    alertOptions.focusConfirm = false;
    return Swal.fire(alertOptions);
  }
}









