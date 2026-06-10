import { Component, inject, model, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ButtonModule } from 'primeng/button';
import { DividerModule } from 'primeng/divider';
import { InputTextModule } from 'primeng/inputtext';
import { FormsModule } from '@angular/forms';
import { MultiSelectModule } from 'primeng/multiselect';
import { InputSwitchModule } from 'primeng/inputswitch';
import { DropdownModule } from 'primeng/dropdown';
import { SliderModule } from 'primeng/slider';
import { environment } from 'src/environments/environment';
import { HttpClient } from '@angular/common/http';
import { ToastService } from '../toast/toast.service';
import { ProjectsComponent } from './projects.component';
import { GraphStore } from '../graph/graph.store';

@Component({
  selector: 'app-settings',
  standalone: true,
  imports: [
    CommonModule, ButtonModule, DividerModule, InputTextModule,
    FormsModule, MultiSelectModule, InputSwitchModule, DropdownModule, SliderModule, ProjectsComponent
  ],
  template: `
    <div class="flex flex-col space-y-6 justify-center w-full bg-white text-black p-4 h-full">
        <app-projects />
        <p-divider />
        <div class="flex items-center justify-between">
          <span>Graph Renderer</span>
          <div class="flex items-center gap-2">
            <span [class.font-bold]="graphStore.graphRenderer() === 'cytoscape'">Cytoscape</span>
            <p-inputSwitch
              [ngModel]="graphStore.graphRenderer() === 'foblex'"
              (ngModelChange)="graphStore.toggleRenderer()" />
            <span [class.font-bold]="graphStore.graphRenderer() === 'foblex'">Foblex</span>
          </div>
        </div>
        @if (graphStore.graphRenderer() === 'foblex') {
          <div class="flex items-center justify-between">
            <span>Layout</span>
            <p-dropdown
              [options]="graphStore.graphLayoutOptions()"
              [(ngModel)]="graphStore.graphLayoutAlgorithm"
              optionLabel="label"
              optionValue="value"
              appendTo="body" />
          </div>
          <div class="flex flex-col space-y-2">
            <div class="flex items-center justify-between">
              <span>Node Repulsion</span>
              <span class="text-sm text-gray-600">{{ graphStore.nodeRepulsion() }}</span>
            </div>
            <p-slider [(ngModel)]="graphStore.nodeRepulsion" [min]="0" [max]="100" [step]="1" />
          </div>
        }
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
  graphStore = inject(GraphStore);
  clearGraph() {
    const url = environment.apiBaseUrl + '/graph/clear/';
    console.log(url);
    console.log(environment)
    this.#http.post(url, {}).subscribe(() => {
      this.#toastService.show('Graph cleared successfully.')
    });
  }
}
