import { Component, computed, effect, inject, model, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { TableModule } from 'primeng/table';
import { FormsModule } from '@angular/forms';
import { CheckboxModule } from 'primeng/checkbox';
import { TabsModule } from 'primeng/tabs';
import { SearchComponent } from "./search.component";
import { ImportComponent } from './import.component';
import { DocumentUploadComponent } from "../graph/doc-upload.component";
import { ProjectsComponent } from './projects.component';


@Component({
  selector: 'app-add-data',
  standalone: true,
  imports: [CommonModule, ButtonModule, InputTextModule, TableModule, 
    FormsModule, CheckboxModule, TabsModule, SearchComponent, ImportComponent, 
    DocumentUploadComponent, ProjectsComponent],
  template: `
    <p-tabs value="0" class="h-full">
      <p-tablist>
          <p-tab value="0">Search</p-tab>
          <p-tab value="1">BibTeX</p-tab>
          <p-tab value="2">Documents</p-tab>
      </p-tablist>
      <p-tabpanels class="h-full">
          <p-tabpanel class="h-full" value="0">
              <app-search />
          </p-tabpanel>
          <p-tabpanel value="1">
              <app-import />
          </p-tabpanel>
            <p-tabpanel value="2">
                <app-doc-upload />
            </p-tabpanel>
      </p-tabpanels>
  </p-tabs>
  `,
  styles: [],
})
export class AddDataComponent {}
