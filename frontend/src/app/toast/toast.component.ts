  import { Component, inject, OnInit, signal } from '@angular/core';
  import { CommonModule } from '@angular/common';
  import { ToastService } from './toast.service';
  
  @Component({
      selector: 'app-toast',
      imports: [CommonModule],
      standalone: true,
      template: `<div *ngIf="display()" class="toast-wrapper">
      <div class="toast-body {{ isError() ? 'toast-body-error' : '' }}">
        {{ message() }}
      </div>
    </div>
    `,
    styles: [`
    .toast-wrapper {
      position: fixed;
      bottom: 100px;
      width: 100%;
      z-index: 9999;
      display: flex;
      align-items: center;
      justify-content: center;
    
      .toast-body {
        min-width: 200px;
        padding: 15px 10px;
        background-color:#ADC04B;
        // border: 2px solid $color-green-1;
        border-radius: 4px;
        display: flex;
        justify-content: space-between;
    
        color: white;
    
        i {
          margin-left: 30px;
          &:hover {
            cursor: pointer;
          }
        }
      }
    
      .toast-body-error {
        background-color: #B30B00;
      }
    }`]
  })
  export class ToastComponent implements OnInit {
    message = signal('');
    display = signal(false);
    isError = signal(false);
    toastService = inject(ToastService);
  
    ngOnInit(): void {
      this.toastService.toastSubject.subscribe(({ message, type }) => {
        this.message.set(message);
        this.isError.set(type === this.toastService.MessageType.Error);
        this.showToast();
      });
    }
  
    showToast() {
      this.display.set(true);
      setTimeout(() => {
        this.display.set(false);
      }, 3 * 1000);
    }
  }
  