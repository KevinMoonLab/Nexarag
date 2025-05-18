import { Component, computed, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ButtonModule } from 'primeng/button';
import { DividerModule } from 'primeng/divider';
import { AddDataComponent } from "./add-data.component";
import { FilterComponent } from './filter.component';
import { SettingsComponent } from './settings.component';
import { ViewportStore } from '../viewport/viewport.store';

@Component({
  selector: 'app-menu',
  standalone: true,
  imports: [CommonModule, ButtonModule, DividerModule, AddDataComponent, FilterComponent, SettingsComponent],
  template: `
    <div class="h-screen text-white flex transition-all duration-300" [ngClass]="{'w-[40rem]': expanded(), 'w-16': !expanded()}">
      <div *ngIf="expanded()" class="flex-grow">
        <ng-container *ngIf="selectedTab() === 0">
          <app-add-data />
        </ng-container>
        <ng-container *ngIf="selectedTab() === 1">
          <app-filter />
        </ng-container>
        <ng-container *ngIf="selectedTab() === 2">
          <app-settings />
        </ng-container>
      </div>

      <div class="bg-gray-800 w-16 flex flex-col items-center border-l border-gray-700 p-2">
        <p-button icon="{{ icon() }}" class="p-button-rounded p-button-text text-white mt-4" (click)="toggleMenu()"></p-button>
        <p-button *ngFor="let tab of tabs; let i = index" 
                  icon="{{ tab.icon }}" 
                  class="p-button-rounded p-button-text text-white mt-6" 
                  (click)="selectTab(i)">
        </p-button>
      </div>
    </div>
  `,
  styles: [],
})
export class MenuComponent {
  expanded = signal(false);
  selectedTab = signal(0);
  viewportStore = inject(ViewportStore);

  icon = computed(() => !this.expanded() ? 'pi pi-angle-right' : 'pi pi-angle-left');

  tabs = [
    { icon: 'pi pi-plus', label: 'Add Data' },
    { icon: 'pi pi-search', label: 'Filter' },
    { icon: 'pi pi-cog', label: 'Settings' },
    { icon: 'pi pi-chart-line', label: 'Plot' }
  ];

  toggleMenu() {
    this.expanded.update(prev => !prev);
  }

  selectTab(index: number) {
    if (index === 3) {
      this.viewportStore.showPlot.update(prev => !prev);
      return;
    }

    this.selectedTab.set(index);
    this.expanded.set(true);
  }
}