import { HttpClient } from "@angular/common/http";
import { computed, effect, inject, Injectable, signal } from "@angular/core";
import { Observable, Subject, switchMap } from "rxjs";
import { AuthorData, Edge, KnowledgeGraph, KnowledgeNode, NodeLabel, PaperData } from "./types";
import { environment } from "src/environments/environment";
import {
    Core,
  } from 'cytoscape';


@Injectable({
    providedIn: 'root',
})
export class GraphStore {
    http = inject(HttpClient);
    graph = signal({
        nodes: [] as KnowledgeNode[],
        edges: [] as Edge[],
    });


    logger = effect(() => console.log(this.graph()));

    searchTerm = signal('');
    filteredGraph = computed(() => {
        const searchTerm = this.searchTerm().toLowerCase();
        if (searchTerm.length === 0) {
            return this.graph();
        }

        const nodes = this.graph().nodes.filter((node) => {
            return (node.label === 'Author' && (node.properties as AuthorData).name.toLowerCase().includes(searchTerm)) 
                || (node.label == 'Paper' && (node.properties as PaperData).title.toLowerCase().includes(searchTerm));
        });

        return {
            nodes,
            edges: []
        };
    }) 

    menuItems = [
        {
            id: 'show-node',
            content: 'Details',
            tooltipText: 'View Node Details',
            selector: 'node',
            onClickFunction: () => this.showNodeDialog.set(true),
            show: false,
        },
    ]

    showNodeDialog = signal(false);
    selectedNodeKey = signal('');
    selectedNode = computed(() => {
        const key = this.selectedNodeKey();
        return this.getNode(key);
    });
    private fetchGraphSubject = new Subject<void>();

    constructor() {
        this.fetchGraphSubject.pipe(switchMap(() => this.fetchGraphFromBackend()))
            .subscribe((graph) => {
                this.graph.set(graph);
            });

        this.fetchGraph();
    }

    fetchGraph(): void {
        this.fetchGraphSubject.next();
    }

    private fetchGraphFromBackend(): Observable<KnowledgeGraph> {
        const url = `${environment.apiBaseUrl}/graph/get/`;
        return this.http.get<KnowledgeGraph>(url);
    }

    graphNodeRepresentations = computed(() => {
        const nodeMap = new Map<string, KnowledgeNode>();
        const typeMap = new Map<string, KnowledgeNode[]>(); 
        const childMap = new Map<string, KnowledgeNode[]>();

        this.graph().nodes.forEach((node) => {
            nodeMap.set(node.id, node);
            
            if (typeMap.has(node.label)) {
                typeMap.get(node.label)?.push(node);
            }
            else {
                typeMap.set(node.label, [node]);
            }
        });

        this.graph().edges.forEach((edge) => {
            const source = edge.source;
            const target = edge.target;
            const node = nodeMap.get(target);
            if (childMap.has(source)) {
                if (node) childMap.get(source)?.push(node);
            }
            else if (node) {
                childMap.set(source, [node]);
            }
        });

        return {
            nodeMap,
            typeMap,
            childMap,
        };
    });

    nodeMap = computed(() => this.graphNodeRepresentations().nodeMap);
    typeMap = computed(() => this.graphNodeRepresentations().typeMap);
    childMap = computed(() => this.graphNodeRepresentations().childMap);

    getNode(id: string): KnowledgeNode | undefined {
        return this.nodeMap().get(id);
    }

    addContextMenu(cy: Core) {
        const ctx = cy.contextMenus({
          menuItems: this.menuItems,
          menuItemClasses: ['custom-context-menu-item'],
          contextMenuClasses: ['custom-context-menu'],
        });
    
        this.addRightClickEvents(cy, ctx);
    }

    private addRightClickEvents(cy: Core, ctx: contextMenus.ContextMenu) {
        cy.on('cxttap', 'node', (event) => {    
          const id = event.target.data()?.id;
          this.selectedNodeKey.set(id);
          ctx.showMenuItem('show-node');
        });
    }
}