import { Component, computed, effect, ElementRef, inject, model, viewChild, ViewEncapsulation } from '@angular/core';
import { CommonModule } from '@angular/common';
import { InputTextModule } from 'primeng/inputtext';
import { FormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { GraphStore } from './graph.store';
import { Core, CoseLayoutOptions, CytoscapeOptions } from 'cytoscape';
import cytoscape from 'cytoscape';

// import elk from 'cytoscape-elk';
import coseBilkent from 'cytoscape-cose-bilkent';
import { AuthorData, KnowledgeNode, PaperData } from './types';
import { NodeDialogComponent } from './node-dialog.component';
import contextMenus from 'cytoscape-context-menus';

cytoscape.use(coseBilkent);
cytoscape.use(contextMenus);

@Component({
  selector: 'app-graph',
  imports: [CommonModule, NodeDialogComponent, InputTextModule, FormsModule, ButtonModule],
  template: `
        <div class="h-screen w-full" #graph id="graph"></div>
        <div class="absolute bottom-4 w-full flex justify-center space-x-4">
            <input id="query" placeholder="Enter query" pInputText [(ngModel)]="query" />
            <p-button label="Submit" (onClick)="submitQuery()" />
        </div>
        <app-node-dialog />
    `,
  styles: [`
    #graph {
        background-color: #fff;
      }
    `],
  encapsulation: ViewEncapsulation.None,
})
export class GraphComponent {
    #graphStore = inject(GraphStore);
    graphElement = viewChild('graph', { read: ElementRef<HTMLDivElement> });
    query = model('');

    private getNodeName(n: KnowledgeNode) {
      if (n.label === 'Author') {
        return (n.properties as AuthorData).name;
      } else {
        return (n.properties as PaperData).title
      }
    }

    submitQuery() {
      this.#graphStore.searchTerm.set(this.query());
    }

    logger = effect(() => console.log(this.cyCore()));

    private getNodeColor(n: KnowledgeNode) {
      if (n.label === 'Author') {
        return '#FF6F61';
      } else {
        return '#6B5B95';
      }
    }

    private truncateName(name: string, maxLength=30): string {
      if (name.length > maxLength) {
        return name.substring(0, maxLength) + '...';
      }
      return name;
    }
  
    cytoscapeGraph = computed(() => {
      const graph = this.#graphStore.filteredGraph();
      const nodes = graph.nodes.map(n => {
        return {
          data: {
            ...n,
            name: this.truncateName(this.getNodeName(n)),
            color: this.getNodeColor(n),
          },
        };
      });
      const edges = graph.edges.map(e => ({ data: e }));
      return { nodes, edges };
    });
  
    cyOptions = computed(() => {
      const ref = this.graphElement();
      if (!ref) {
        return null;
      }
  
      const options: CytoscapeOptions = {
        container: ref.nativeElement,
        elements: this.cytoscapeGraph(),
        layout: {
            name: 'cose',
            nodeRepulsion: () => 40000,
        } as CoseLayoutOptions,
        style: [
          {
            selector: 'node',
            style: {
              'label': 'data(name)',
              'background-color': 'data(color)',
              'text-valign': 'center',
              'text-halign': 'center',
              'color': '#000',
              'font-size': '12px',
              'border-width': '1px',
              'border-color': '#d3d3d3'
            }
          },
          {
            selector: 'edge',
            style: {
              'width': 2,
              'line-color': '#d3d3d3',
              'curve-style': 'bezier'
            }
          }
        ],
      };
  
      return options;
    });
  
    cyCore = computed(() => {
      const options = this.cyOptions();
      if (!options) {
          return null;
      }  
      const cy: Core = cytoscape(options);
      this.#graphStore.addContextMenu(cy);
      return cy;
    });
}
