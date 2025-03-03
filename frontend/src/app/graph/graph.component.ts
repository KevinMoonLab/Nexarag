import { Component, computed, effect, ElementRef, inject, model, signal, untracked, viewChild, ViewEncapsulation } from '@angular/core';
import { CommonModule } from '@angular/common';
import { InputTextModule } from 'primeng/inputtext';
import { FormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { GraphStore } from './graph.store';
import { Core, CoseLayoutOptions, CytoscapeOptions, StylesheetJson } from 'cytoscape';
import cytoscape from 'cytoscape';
import coseBilkent from 'cytoscape-cose-bilkent';
import { KnowledgeNode } from './types';
import { NodeDialogComponent } from './node-dialog.component';
import contextMenus from 'cytoscape-context-menus';
import { MenuComponent } from "../menu/menu.component";
import { ChatMenuComponent } from "../chat/chat-menu.component";
import { DocumentDialogComponent } from "./doc-dialog.component";

cytoscape.use(coseBilkent);
cytoscape.use(contextMenus);

@Component({
  selector: 'app-graph',
  imports: [CommonModule, InputTextModule, FormsModule, ButtonModule, MenuComponent, NodeDialogComponent, ChatMenuComponent, DocumentDialogComponent],
  template: `
        <div class="relative h-screen w-full flex">
          <div class="absolute top-0 left-0 h-full z-50">
            <app-menu />
          </div>
          <div class="absolute top-0 right-0 h-full z-50">
            <app-chat-menu />
          </div>
          <div class="flex-grow h-screen w-full" #graph id="graph"></div>
        </div>
        <app-node-dialog />
        <app-doc-dialog />
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

    constructor() {
      effect(() => {
        this.cyCore();
      });
    }

    destroyGraph() {
      const cy = this.cyCore();
      if (cy) {
        cy.destroy();
      }
    }

    private getNodeColor(n: KnowledgeNode) {
      if (n.label === 'Author') {
        return '#D72638';
      } else if (n.label === 'Paper') {
        return '#3E92CC';
      } else if (n.label === 'Journal') {
        return '#6BBF59'; 
      } else if (n.label === 'PublicationVenue') {
        return '#F4A261'; 
      } else {
        return '#4A4A4A'; 
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
      const maxDegree = this.#graphStore.maxDegree();
      const degreeMap = this.#graphStore.degreeMap();
      const nodes = graph.nodes
        .map(n => {
          return {
            data: {
              id: n.id,
              name: this.truncateName(this.#graphStore.getNodeName(n)),
              color: this.getNodeColor(n),
              weight: 50 * (Math.max(degreeMap.get(n.id) || 5, 5)) / maxDegree,
            },
          };
        });
      const edges = graph.edges.map(e => ({ data: e }));
      return { nodes, edges };
    });

    styleSheet = computed<StylesheetJson>(() => {
      const weightNodes = this.#graphStore.weightNodes();
      if (weightNodes) {
        return [
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
              'border-color': '#d3d3d3',
              'width': 'data(weight)',
              'height': 'data(weight)',
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
        ];
      } else {
        return [
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
        ]
      }


    })
  
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
            nodeRepulsion: () => 70000,
        } as CoseLayoutOptions,
        style: this.styleSheet(),
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
