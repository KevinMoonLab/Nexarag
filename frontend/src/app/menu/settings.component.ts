import { Component, inject, model, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ButtonModule } from 'primeng/button';
import { DividerModule } from 'primeng/divider';
import { InputTextModule } from 'primeng/inputtext';
import { FormsModule } from '@angular/forms';
import { MultiSelectModule } from 'primeng/multiselect';
import { InputSwitchModule } from 'primeng/inputswitch';
import { GraphStore } from '../graph/graph.store';
import { environment } from 'src/environments/environment';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-settings',
  standalone: true,
  imports: [
    CommonModule, ButtonModule, DividerModule, InputTextModule, 
    FormsModule, MultiSelectModule, InputSwitchModule
  ],
  template: `
    <div class="flex flex-col space-y-6 h-screen w-full bg-white text-black p-4">
        <p-button label="Clear Graph" severity="danger" (click)="clearGraph()" />
    </div>
    <p-divider />
  `,
  styles: [],
})
export class SettingsComponent {
  #http = inject(HttpClient);
  clearGraph() {
    const url = environment.apiBaseUrl + '/graph/clear';
    this.#http.post(url, {}).subscribe(() => {
      console.log('Graph cleared');
    });
  }
}
