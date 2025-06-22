import { HttpClient } from "@angular/common/http";
import { computed, effect, inject, Injectable, signal } from "@angular/core";
import { Observable, Subject, switchMap } from "rxjs";
import { AuthorData, Edge, JournalData, KnowledgeGraph, KnowledgeNode, PaperData, PublicationVenueData, DocumentData } from "./types";
import { environment } from "src/environments/environment";
import {
    Core,
  } from 'cytoscape';
import { ToastService } from "../toast/toast.service";
import { EventService } from "../events.service";


@Injectable({
    providedIn: 'root',
})
export class GraphStore {
    http = inject(HttpClient);
    toastService = inject(ToastService);
    events = inject(EventService);
    graph = signal({
        nodes: [] as KnowledgeNode[],
        edges: [] as Edge[],
    });
    searchTerm = signal('');
    weightNodes = signal(false);

    logger = effect(() => console.log('GraphStore: graph updated', this.graph()));

    filteredGraph = computed(() => {
        const selectedNodeTypes = this.selectedDisplayFilters();
        const searchTerm = this.searchTerm();
        let nodes = [] as KnowledgeNode[];
        if (searchTerm) {
            const searchTermLower = searchTerm.toLowerCase();
            nodes = this.graph().nodes.filter((node) => {
                const nodeName = this.getNodeName(node).toLowerCase();
                return selectedNodeTypes.includes(node.label) && nodeName.includes(searchTermLower);
            });
        } else {
            nodes = this.graph().nodes.filter(n => selectedNodeTypes.includes(n.label));
        }
        const nodeIds = new Set(nodes.map((node) => node.id));
        const edges = this.graph().edges.filter((edge) => nodeIds.has(edge.source) && nodeIds.has(edge.target));
        return { nodes, edges } as KnowledgeGraph;
    });

    degreeMap = computed(() => {
        const degreeMap = new Map<string, number>();
        const parentNodes = this.parentMap();
        const childNodes = this.childMap();

        this.graph().nodes.forEach((node) => {
            const parents = parentNodes.get(node.id) || [];
            const children = childNodes.get(node.id) || [];
            const allIds = [...parents.map(p => p.id), ...children.map(c => c.id)];
            const uniqueIds = new Set(allIds);
            degreeMap.set(node.id, uniqueIds.size);
        });

        return degreeMap;
    });

    private plotResizeSubject = new Subject<void>();
    readonly plotResize = this.plotResizeSubject.asObservable();
  
    showPlot = signal(false);
  
    emitPlotResize() {
      this.plotResizeSubject.next();
    }

    maxDegree = computed(() => this.degreeMap() ? Math.max(...Array.from(this.degreeMap().values())) : 0);

    selectedDisplayFilters = signal(['Paper', 'Journal', 'Document', 'Author']);
    displayFilterOptions = signal([
      { label: 'Author', value: 'Author' },
      { label: 'Paper', value: 'Paper' },
      { label: 'Journal', value: 'Journal' },
      { label: 'Publication Venue', value: 'PublicationVenue' },
      { label: 'Document', value: 'Document' },
    ]);

    selectedAuthors = signal([] as string[]);
    authorOptions = computed(() => {
        const authors = this.typeMap().get('Author') || [];
        return authors.map((author) => ({
            label: (author.properties as AuthorData).name,
            value: author.id,
        }));
    })

    nodeMenuItems = [
        {
            id: 'show-node',
            content: 'Details',
            tooltipText: 'View Node Details',
            selector: 'node',
            onClickFunction: () => this.showNodeDialog.set(true),
            show: true,
        },
        {
            id: 'add-citations',
            content: 'Add Citations',
            tooltipText: 'Add Citations',
            selector: 'node',
            onClickFunction: () => this.addCitations(),
            show: true,
        },        
        {
            id: 'add-references',
            content: 'Add References',
            tooltipText: 'Add References',
            selector: 'node',
            onClickFunction: () => this.addReferences(),
            show: true,
        },
        {
            id: 'add-documents',
            content: 'Add Documents',
            tooltipText: 'Add Documents',
            selector: 'node',
            onClickFunction: () => this.showAddDocuments(),
            show: true,
        }
    ]

    canvasMenuItems = [
        {
            id: 'bulk-add-documents',
            content: 'Bulk Add Documents',
            tooltipText: 'Add Documents in Bulk',
            selector: 'core', // 'core' targets the canvas/background
            onClickFunction: () => this.bulkAddDocuments(),
            show: true,
        },
        {
            id: 'refresh-graph',
            content: 'Refresh Graph',
            tooltipText: 'Refresh the entire graph',
            selector: 'core',
            onClickFunction: () => this.refreshGraph(),
            show: true,
        }
    ];

    showAddDocuments() {
        this.showDocumentDialog.set(true);
    }

    addCitations() {
        const selectedNode = this.selectedNode();
        if (!selectedNode) return;
        if (selectedNode.label !== 'Paper') return;
        const paperId = (selectedNode.properties as PaperData).paper_id;
        const url = `${environment.apiBaseUrl}/papers/citations/add/`;
        this.http.post(url, [paperId]).subscribe(() => {
            this.toastService.show('Building citation graph...');
        });
    }

    addReferences() {
        const selectedNode = this.selectedNode();
        if (!selectedNode) return;
        if (selectedNode.label !== 'Paper') return;
        const paperId = (selectedNode.properties as PaperData).paper_id;
        const url = `${environment.apiBaseUrl}/papers/references/add/`;
        this.http.post(url, [paperId]).subscribe(() => {
            this.toastService.show('Building reference graph...');

        });
    }

    getNodeName(n: KnowledgeNode) {
        if (n.label === 'Author') {
            return (n.properties as AuthorData).name;
        } else if (n.label === 'Paper') {
            return (n.properties as PaperData).title
        } else if (n.label === 'Journal') {
            return (n.properties as JournalData).name;
        } else if (n.label === 'PublicationVenue') {
            return (n.properties as PublicationVenueData).name;
        } else if (n.label === 'Document') {
            return (n.properties as DocumentData).name;
        } else {
            return 'No Name';
        }
    }

    showNodeDialog = signal(false);
    showDocumentDialog = signal(false);
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

        this.events.events$.subscribe((event) => {
            if (event.type === 'graph_updated') {
                this.toastService.show('Graph updated!');
                this.fetchGraph();
            }
        });
    }

    fetchGraph(): void {
        this.fetchGraphSubject.next();
    }

    private fetchGraphFromBackend(): Observable<KnowledgeGraph> {
        const url = `${environment.apiBaseUrl}/graph/get/`;
        return this.http.get<KnowledgeGraph>(url);
    }

    public addNodes(nodes: KnowledgeNode[]) {
        this.graph.update((prevGraph) => ({ ...prevGraph, nodes: [...prevGraph.nodes, ...nodes] }));
    }

    graphNodeRepresentations = computed(() => {
        const nodeMap = new Map<string, KnowledgeNode>();
        const typeMap = new Map<string, KnowledgeNode[]>(); 
        const childMap = new Map<string, KnowledgeNode[]>();
        const parentMap = new Map<string, KnowledgeNode[]>();

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

            const parent = nodeMap.get(source);
            if (parentMap.has(target)) {
                if (parent) parentMap.get(target)?.push(parent);
            }
            else if (parent) {
                parentMap.set(target, [parent]);
            }
        });

        return {
            nodeMap,
            typeMap,
            childMap,
            parentMap,
        };
    });

    nodeMap = computed(() => this.graphNodeRepresentations().nodeMap);
    typeMap = computed(() => this.graphNodeRepresentations().typeMap);
    childMap = computed(() => this.graphNodeRepresentations().childMap);
    parentMap = computed(() => this.graphNodeRepresentations().parentMap);

    getNode(id: string): KnowledgeNode | undefined {
        return this.nodeMap().get(id);
    }

    setSelectedPaper(id: string) {
        const paper = this.graph().nodes
            .filter(n => n.label === 'Paper')
            .find(p => (p.properties as PaperData).paper_id === id);

        if (paper) {
            this.selectedNodeKey.set(paper.id);
        }
    }

    bulkAddDocuments() {
        this.showDocumentDialog.set(true);
        this.selectedNodeKey.set('');
    }

    refreshGraph() {
        this.fetchGraph();
    }

    addContextMenu(cy: Core) {
        const allMenuItems = [...this.nodeMenuItems, ...this.canvasMenuItems];
        
        const ctx = cy.contextMenus({
            menuItems: allMenuItems,
            menuItemClasses: ['custom-context-menu-item'],
            contextMenuClasses: ['custom-context-menu'],
        });

        this.addRightClickEvents(cy, ctx);
    }

    private addRightClickEvents(cy: Core, ctx: contextMenus.ContextMenu) {
        cy.on('cxttap', 'node', (event) => {    
            const id = event.target.data()?.id;
            this.selectedNodeKey.set(id);
            
            this.canvasMenuItems.forEach(item => {
                ctx.hideMenuItem(item.id);
            });
            
            this.nodeMenuItems.forEach(item => {
                ctx.showMenuItem(item.id);
            });
        });

        // Handle right-click on canvas (background)
        cy.on('cxttap', (event) => {
            if (event.target === cy) {
                this.nodeMenuItems.forEach(item => {
                    ctx.hideMenuItem(item.id);
                });
                
                this.canvasMenuItems.forEach(item => {
                    ctx.showMenuItem(item.id);
                });
            }
        });
    }


}