import { Component, signal, model, ViewEncapsulation, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TextareaModule } from 'primeng/textarea';
import { InputTextModule } from 'primeng/inputtext';
import { ButtonModule } from 'primeng/button';
import { DropdownModule } from 'primeng/dropdown';
import { TableModule } from 'primeng/table';
import { HttpClient } from '@angular/common/http';
import { environment } from 'src/environments/environment';
import { ToastService } from '../toast/toast.service';

interface PromptItem {
  label: string;
  prompt: string;
}

@Component({
  selector: 'app-plot-controls',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    TextareaModule,
    InputTextModule,
    ButtonModule,
    DropdownModule,
    TableModule
  ],
  template: `
    <div class="p-8 max-w-7xl mx-auto space-y-8 min-h-full">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
        <!-- Settings Column -->
        <section class="space-y-4">
          <h2 class="text-xl font-semibold text-gray-800">Configuration</h2>

          <label class="block mb-1 text-sm font-medium text-gray-700">
            Color Variable
          </label>
          <p-dropdown
            [options]="colorVariables"
            [(ngModel)]="selectedColorVariable"
            placeholder="Select color variable"
            optionLabel="label"
            optionValue="value"
            class="w-full"
          ></p-dropdown>
        </section>

        <!-- Prompt + Label Input -->
        <section class="space-y-4">
          <h2 class="text-xl font-semibold text-gray-800">Prompt Input</h2>

          <input
            pInputText
            [(ngModel)]="currentLabel"
            placeholder="Label"
            class="w-full p-3 border rounded-md shadow-sm"
          />

          <textarea
            pInputTextarea
            [(ngModel)]="currentPrompt"
            rows="1"
            placeholder="Prompt"
            class="w-full p-3 border rounded-md shadow-sm"
          ></textarea>

          <button
            pButton
            type="button"
            label="Add"
            icon="pi pi-plus"
            (click)="addPrompt()"
            [disabled]="!canAdd()"
            class="bg-blue-600 text-white px-4 py-2 rounded shadow hover:bg-blue-700 disabled:opacity-50"
          ></button>

          <!-- Grid -->
          <p-table
            [value]="prompts()"
            class="p-datatable-sm"
            *ngIf="prompts().length"
          >
            <ng-template pTemplate="header">
              <tr>
                <th>Label</th>
                <th>Prompt</th>
                <th style="width: 4rem"></th>
              </tr>
            </ng-template>

            <ng-template pTemplate="body" let-item let-rowIndex="rowIndex">
              <tr>
                <td>{{ item.label }}</td>
                <td>{{ item.prompt }}</td>
                <td>
                  <button
                    pButton
                    icon="pi pi-trash"
                    class="p-button-text text-red-500"
                    (click)="removePrompt(rowIndex)"
                  ></button>
                </td>
              </tr>
            </ng-template>
          </p-table>
        </section>
      </div>

      <!-- Submit -->
      <div class="border-t pt-6 flex justify-center">
        <button
          pButton
          label="Submit"
          icon="pi pi-send"
          (click)="submit()"
          [disabled]="!isFormValid()"
          class="bg-green-600 text-white px-6 py-3 rounded shadow hover:bg-green-700 disabled:opacity-50"
        ></button>
      </div>
    </div>
  `,
  encapsulation: ViewEncapsulation.None,
  styles: []
})
export class PlotControlComponent {
  #http = inject(HttpClient);
  #toastService = inject(ToastService);

  // State
  prompts = signal<PromptItem[]>([]);
  currentPrompt = model('');
  currentLabel = model('');

  // Dropdown
  selectedColorVariable = model<string | null>(null);
  colorVariables = [
    { label: 'Labels', value: 'labels' },
    { label: 'Citation Count', value: 'citationCount' },
    { label: 'Date', value: 'date' }
  ];

  canAdd() {
    return this.currentPrompt().trim() && this.currentLabel().trim();
  }

  addPrompt() {
    this.prompts.update(p => [
      ...p,
      { prompt: this.currentPrompt().trim(), label: this.currentLabel().trim() }
    ]);
    this.currentPrompt.set('');
    this.currentLabel.set('');
  }

  removePrompt(index: number) {
    this.prompts.update(p => p.filter((_, i) => i !== index));
  }

  isFormValid() {
    return this.prompts().length && this.selectedColorVariable();
  }

  clear() {
    this.prompts.set([]);
    this.currentPrompt.set('');
    this.currentLabel.set('');
    this.selectedColorVariable.set(null);
  }

  submit() {
    const cmd = {
      queries: this.prompts().map(p => p.prompt),
      labels: this.prompts().map(p => p.label),
      color_var: this.selectedColorVariable()
    };
    
    this.#http.post(environment.apiBaseUrl + '/viz/plot/', cmd)
      .subscribe(res => {
        this.#toastService.show('Submitted plot data.');
        this.clear();
      });
  }
}
