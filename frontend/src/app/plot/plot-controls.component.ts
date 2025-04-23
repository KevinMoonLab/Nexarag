import { Component, signal, model, ViewEncapsulation } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TextareaModule } from 'primeng/textarea';
import { ButtonModule } from 'primeng/button';
import { DropdownModule } from 'primeng/dropdown';

@Component({
  selector: 'app-plot-controls',
  standalone: true,
  imports: [CommonModule, FormsModule, TextareaModule, ButtonModule, DropdownModule],
  template: `
    <div class="p-8 max-w-7xl mx-auto space-y-8 min-h-full">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-8">

        <!-- Prompt Input -->
        <section class="space-y-4">
          <h2 class="text-xl font-semibold text-gray-800">Prompt Input</h2>

          <textarea
            pInputTextarea
            [(ngModel)]="currentPrompt"
            name="promptInput"
            rows="1"
            autoResize="false"
            placeholder="Enter a prompt and click 'Add Prompt'"
            class="w-full p-3 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          ></textarea>

          <button
            pButton
            type="button"
            label="Add Prompt"
            icon="pi pi-plus"
            (click)="addPrompt()"
            [disabled]="!currentPrompt().trim()"
            class="bg-blue-600 text-white px-4 py-2 rounded shadow hover:bg-blue-700 disabled:opacity-50"
          > </button>

          <ul class="space-y-3">
            <li *ngFor="let prompt of prompts(); let i = index">
              <div class="flex justify-between items-start bg-gray-100 p-4 rounded shadow-sm">
                <pre class="whitespace-pre-wrap break-words text-gray-800 w-full pr-4">{{ prompt }}</pre>
                <button
                  pButton
                  icon="pi pi-trash"
                  (click)="removePrompt(i)"
                  class="p-button-text text-red-500 hover:text-red-700"
                  aria-label="Remove Prompt"
                ></button>
              </div>
            </li>
          </ul>
        </section>

        <!-- Settings Column -->
        <section class="space-y-4">
          <h2 class="text-xl font-semibold text-gray-800">Configuration</h2>

          <div class="space-y-4">
            <div>
              <label class="block mb-1 text-sm font-medium text-gray-700">Color Variable</label>
              <p-dropdown
                [options]="colorVariables"
                [(ngModel)]="selectedColorVariable"
                placeholder="Select color variable"
                optionLabel="label"
                class="w-full"
              ></p-dropdown>
            </div>
          </div>
        </section>

      </div>

      <!-- Submit Button Row -->
      <div class="border-t pt-6 w-full flex justify-center">
        <button
          pButton
          type="button"
          label="Submit"
          icon="pi pi-send"
          (click)="submit()"
          [disabled]="!isFormValid()"
          class="bg-green-600 text-white px-6 py-3 rounded shadow hover:bg-green-700 disabled:opacity-50"
        > </button>
      </div>
    </div>
  `,
  encapsulation: ViewEncapsulation.None,
  styles: []
})
export class PlotControlComponent {
  // State
  prompts = signal<string[]>([]);
  currentPrompt = model('');

  // Dropdown Selections
  selectedColorVariable = model<string | null>(null);

  // Options
  colorVariables = [
    { label: 'Labels', value: 'labels' },
    { label: 'Citation Count', value: 'citationCount' },
    { label: 'Date', value: 'date' },
  ];

  addPrompt() {
    const trimmed = this.currentPrompt().trim();
    if (trimmed) {
      this.prompts.update(p => [...p, trimmed]);
      this.currentPrompt.set('');
    }
  }

  removePrompt(index: number) {
    this.prompts.update(p => p.filter((_, i) => i !== index));
  }

  isFormValid(): boolean {
    return (
      this.prompts().length > 0 && this.selectedColorVariable() !== null
    );
  }

  submit() {
    const payload = {
      prompts: this.prompts(),
      colorVariable: this.selectedColorVariable(),
    };
  }
}
