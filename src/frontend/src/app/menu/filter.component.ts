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
    <div class="flex flex-col space-y-6 h-screen w-full bg-white text-black px-4 py-6">

      <!-- Search Bar -->
      <div class="flex flex-col space-y-2">
        <label class="text-sm font-semibold text-black">Search</label>
        <input
          type="text"
          pInputText
          [(ngModel)]="query"
          class="w-full rounded-md border border-gray-400"
          placeholder="Search papers and authors..."
        />
      </div>

      <p-divider />

      <!-- Select Filters to Display -->
      <div class="flex flex-col space-y-2">
        <label class="text-sm font-semibold text-black">Visible Nodes</label>
        <p-multiSelect
          [(ngModel)]="graphStore.selectedDisplayFilters"
          [options]="graphStore.displayFilterOptions()"
          placeholder="Visible nodes"
          class="w-full"
        ></p-multiSelect>
      </div>

      <p-divider />

      <!-- Toggle Node Weighting -->
      <div class="flex flex-col space-y-2">
        <label class="text-sm font-semibold text-black">Node Weighting</label>
        <div class="flex items-center justify-between">
          <span>Enable weighting</span>
          <p-inputSwitch [(ngModel)]="nodeWeighting"></p-inputSwitch>
        </div>
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
