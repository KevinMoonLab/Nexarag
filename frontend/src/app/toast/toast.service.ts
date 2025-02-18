import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class ToastService {
  MessageType = {
    Error: 'error',
    Success: 'success',
  };

  toastSubject: Subject<{ message: string; type: string }> = new Subject();

  show(message: string) {
    this.toastSubject.next({
      message: message,
      type: this.MessageType.Success,
    });
  }

  showError(message: string) {
    this.toastSubject.next({ message: message, type: this.MessageType.Error });
  }
}
