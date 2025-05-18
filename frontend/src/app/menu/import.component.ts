import { Component, computed, effect, inject, model, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { TableModule } from 'primeng/table';
import { FormsModule } from '@angular/forms';
import { CheckboxModule } from 'primeng/checkbox';
import { AddDataStore } from './add-data.store';
import { ToastService } from '../toast/toast.service';
import { TabsModule } from 'primeng/tabs';
import { HttpClient } from '@angular/common/http';
import { environment } from 'src/environments/environment';
import { GraphStore } from '../graph/graph.store';
import { KnowledgeGraph } from '../graph/types';


@Component({
  selector: 'app-import',
  standalone: true,
  imports: [CommonModule, ButtonModule, InputTextModule, TableModule, FormsModule, CheckboxModule, TabsModule],
  template: `
    <div class="flex flex-col items-center space-y-4 p-4">
      <h2 class="text-xl font-semibold">Add Papers from BibTex File</h2>
      
      <textarea 
        [(ngModel)]="bibtexData"

        rows="15"
        class="w-full max-w-4xl p-3 border border-gray-300 rounded resize-y"
        placeholder="Paste your .bib file content here..."
      ></textarea>

      <div class="flex space-x-4 justify-center">
        <p-button label="Clear" (onClick)="clear()" severity="secondary"></p-button>
        <p-button label="Submit" (onClick)="submit()" severity="primary"></p-button>
      </div>
    </div>
  `,
  styles: [],
})
export class ImportComponent {
  toastService = inject(ToastService);
  graphStore = inject(GraphStore);
  http = inject(HttpClient);
  
  bibtexData = model();

  clear() {
    this.bibtexData.set('');
  }

  submit() {
    const uri = environment.apiBaseUrl + "/papers/bibtex";
    this.http.post<KnowledgeGraph>(uri, { bibtex: this.bibtexData() })
      .subscribe(res => {
        this.clear();
        console.log(res);
        this.graphStore.addNodes(res.nodes);
        this.toastService.show(`Successfully added ${res.nodes.length} papers.`);
      });
  }
}
