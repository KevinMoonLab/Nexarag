import { Component, inject, model, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ButtonModule } from 'primeng/button';
import { DividerModule } from 'primeng/divider';
import { InputTextModule } from 'primeng/inputtext';
import { FormsModule } from '@angular/forms';
import { MultiSelectModule } from 'primeng/multiselect';
import { InputSwitchModule } from 'primeng/inputswitch';
import { environment } from 'src/environments/environment';
import { HttpClient } from '@angular/common/http';
import { ToastService } from '../toast/toast.service';
import { ProjectsComponent } from './projects.component';

@Component({
  selector: 'app-settings',
  standalone: true,
  imports: [
    CommonModule, ButtonModule, DividerModule, InputTextModule, 
    FormsModule, MultiSelectModule, InputSwitchModule, ProjectsComponent
  ],
  template: `
    <div class="flex flex-col space-y-6 justify-center w-full bg-white text-black p-4 h-full">
        <app-projects />
        <p-divider />
        <p-button label="Clear Current Graph" severity="danger" (click)="clearGraph()" />
    </div>
    <p-divider />
  `,
  styles: [],
})
export class SettingsComponent {
  #http = inject(HttpClient);
  #toastService = inject(ToastService);
  clearGraph() {
    const url = environment.apiBaseUrl + '/graph/clear/';
    console.log(url);
    console.log(environment)
    this.#http.post(url, {}).subscribe(() => {
      this.#toastService.show('Graph cleared successfully.')
    });
  }
}
