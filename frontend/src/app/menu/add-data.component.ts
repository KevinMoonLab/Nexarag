import { Component, computed, effect, inject, model, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { TableModule } from 'primeng/table';
import { FormsModule } from '@angular/forms';
import { CheckboxModule } from 'primeng/checkbox';
import { AddDataStore } from './add-data.store';
import { ToastService } from '../toast/toast.service';

@Component({
  selector: 'app-add-data',
  standalone: true,
  imports: [CommonModule, ButtonModule, InputTextModule, TableModule, FormsModule, CheckboxModule],
  template: `
    <div class="flex flex-col space-y-4">
      <div class="flex space-x-2">
        <input type="text" pInputText [(ngModel)]="query" class="w-full p-4 rounded-md" placeholder="Search Semantic Scholar..." />
        <p-button label="Search" icon="pi pi-search" (click)="search()" class="p-button-primary"></p-button>
      </div>

      <p-table 
        *ngIf="searchResults().length > 0 || loading()" 
        [scrollable]="true" 
        [scrollHeight]="'40rem'" 
        [value]="searchResults()" 
        [loading]="loading()"
        class="shadow-md rounded-lg">
        <ng-template pTemplate="header">
          <tr>
            <th class="text-center">
              Select
            </th>
            <th class="text-left">Title</th>
            <th class="text-left">Year</th>
          </tr>
        </ng-template>
        <ng-template pTemplate="body" let-paper>
          <tr>
            <td class="text-center">
              <p-checkbox [(ngModel)]="paper.selected" [binary]="true"></p-checkbox>
            </td>
            <td>{{ paper.title }}</td>
            <td>{{ paper.year }}</td>
          </tr>
        </ng-template>
      </p-table>

      <!-- No results message -->
      <div *ngIf="searchResults().length === 0 && query" class="text-center text-gray-500">
        No results found.
      </div>

      <div *ngIf="searchResults().length > 0" class="flex flex-row justify-center align-center space-x-4 mt-4">
        <p-button label="Clear" severity="danger" (click)="clear()" />
        <p-button label="Add Data" icon="pi pi-plus" (click)="addData()"></p-button>
      </div>

    </div>
  `,
  styles: [],
})
export class AddDataComponent {
  #store = inject(AddDataStore);
  #toastService = inject(ToastService);
  loading = this.#store.loading;

  query = model('');
  searchResults = computed(() => this.#store.searchResults().map(p => ({ ...p, selected: signal(false) })));

  search() {
    this.#store.search(this.query());
  }

  clearSearch() {
    this.query.set('');
    this.#store.clearResults();
  }

  selectedPapers = computed(() => this.searchResults().filter(p => p.selected()));

  addData() {
    const paperIds = this.selectedPapers().map(p => p.paperId);
    this.#store.addPapersToGraph(paperIds).subscribe(() => {
      this.clearSearch();
      this.#toastService.show('Adding data to graph...');
    });
  }

  clear() {
    this.clearSearch();
  }
}
