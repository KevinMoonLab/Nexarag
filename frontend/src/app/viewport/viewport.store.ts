import { HttpClient } from "@angular/common/http";
import { computed, effect, inject, Injectable, signal } from "@angular/core";
import { Observable, Subject, switchMap } from "rxjs";
import { environment } from "src/environments/environment";
import { ToastService } from "../toast/toast.service";
import { EventService } from "../events.service";


@Injectable({
  providedIn: 'root',
})
export class ViewportStore {
  private plotResizeSubject = new Subject<void>();
  readonly plotResize = this.plotResizeSubject.asObservable();

  showPlot = signal(false);

  emitPlotResize() {
    this.plotResizeSubject.next();
  }
}