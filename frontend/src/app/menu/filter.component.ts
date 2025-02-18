import { Component, inject, model, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ButtonModule } from 'primeng/button';
import { DividerModule } from 'primeng/divider';
import { InputTextModule } from 'primeng/inputtext';
import { FormsModule } from '@angular/forms';
import { MultiSelectModule } from 'primeng/multiselect';
import { InputSwitchModule } from 'primeng/inputswitch';
import { GraphStore } from '../graph/graph.store';

@Component({
  selector: 'app-filter',
  standalone: true,
  imports: [
    CommonModule, ButtonModule, DividerModule, InputTextModule, 
    FormsModule, MultiSelectModule, InputSwitchModule
  ],
  template: `
    <div class="flex flex-col space-y-6">
      
      <!-- Search Bar -->
      <div class="flex space-x-4 items-center">
        <input type="text" pInputText [(ngModel)]="query" class="w-full rounded-md border border-gray-400" placeholder="Search papers and authors..." />
      </div>

      <p-divider />

      <!-- Select Filters to Display -->
      <div class="flex flex-col space-y-3">
        <p-multiSelect [(ngModel)]="graphStore.selectedDisplayFilters" [options]="graphStore.displayFilterOptions()" 
                       placeholder="Visible nodes" class="w-full"></p-multiSelect>
      </div>

      <p-divider />

      <!-- Toggle Node Weighting -->
      <div class="flex items-center justify-between">
        <span class="font-semibold">Node Weighting:</span>
        <p-inputSwitch [(ngModel)]="nodeWeighting"></p-inputSwitch>
      </div>

      <p-divider />

    </div>
  `,
  styles: [],
})
export class FilterComponent {
  graphStore = inject(GraphStore);
  query = this.graphStore.searchTerm;
  nodeWeighting = this.graphStore.weightNodes;
}
