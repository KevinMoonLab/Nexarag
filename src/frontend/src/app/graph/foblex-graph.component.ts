import { Component, computed, effect, inject, signal, untracked, viewChild } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { CommonModule } from '@angular/common';
import { ContextMenu, ContextMenuModule } from 'primeng/contextmenu';
import {
    EFLayoutMode,
    FCanvasComponent,
    FFlowComponent,
    FFlowModule,
    provideFLayout,
} from '@foblex/flow';
import { ElkLayoutEngine } from '@foblex/flow-elk-layout';
import { GraphStore } from './graph.store';
import { GraphLayoutAlgorithm, GraphLayoutService, NodePosition } from './graph-layout.service';
import { NodeDialogComponent } from './node-dialog.component';
import { DocumentDialogComponent } from './doc-dialog.component';

/**
 * Experimental Foblex Flow renderer for the knowledge graph. It is an
 * alternative to {@link GraphComponent} (cytoscape) and reads the exact same
 * {@link GraphStore}, so selection, filters, search, dialogs and plot mode stay
 * in sync no matter which renderer the viewport toggle selects.
 *
 * Foblex has no built-in force layout, so positions come from the ELK engine
 * (FORCE algorithm) via {@link GraphLayoutService}, and the right-click menus
 * are rebuilt with PrimeNG's ContextMenu off the store's shared menu actions.
 */
@Component({
    selector: 'app-foblex-graph',
    imports: [CommonModule, FFlowModule, ContextMenuModule, NodeDialogComponent, DocumentDialogComponent],
    providers: [provideFLayout(ElkLayoutEngine, { mode: EFLayoutMode.MANUAL }), GraphLayoutService],
    template: `
        <p-contextMenu #nodeMenu [model]="store.nodeMenuItemsPng()" appendTo="body" />
        <p-contextMenu #canvasMenu [model]="store.canvasMenuItemsPng()" appendTo="body" />

        <f-flow fDraggable (contextmenu)="onCanvasContext($event)" (fFullRendered)="onRendered()">
            <f-canvas fZoom>
                @for (edge of renderEdges(); track edge.id) {
                    <f-connection
                        [fOutputId]="edge.source"
                        [fInputId]="edge.target"
                        fType="bezier"
                        fReassignDisabled
                        fSelectionDisabled />
                }
                @for (node of displayNodes(); track node.id) {
                    <div
                        fNode
                        [fNodeId]="node.id"
                        [fNodePosition]="node.position"
                        (fNodePositionChange)="onNodeMoved(node.id, $event)"
                        fNodeInput
                        [fInputId]="node.id"
                        fInputMultiple
                        fInputDisabled
                        fNodeOutput
                        [fOutputId]="node.id"
                        fOutputMultiple
                        fOutputDisabled
                        class="kg-node"
                        [class.selected]="node.id === selectedId()"
                        [style.--kg-accent]="node.color"
                        (click)="onNodeClick(node.id)"
                        (contextmenu)="onNodeContext($event, node.id)">
                        <span class="kg-node__label">{{ node.name }}</span>
                    </div>
                }
            </f-canvas>
        </f-flow>

        <app-node-dialog />
        <app-doc-dialog />
    `,
    styles: [`
        :host {
            display: block;
            width: 100%;
            height: 100%;
            background-color: #fff;
        }
        :host ::ng-deep f-flow,
        :host ::ng-deep f-canvas {
            width: 100%;
            height: 100%;
        }
        .kg-node {
            display: flex;
            align-items: center;
            box-sizing: border-box;
            min-width: 96px;
            max-width: 240px;
            min-height: 48px;
            padding: 10px 14px;
            background-color: #fff;
            border: 1px solid #d8dce1;
            border-left: 5px solid var(--kg-accent, #4a4a4a);
            border-radius: 10px;
            color: #1f2933;
            font-size: 13px;
            line-height: 1.3;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.12);
            cursor: pointer;
        }
        .kg-node.selected {
            border-color: #ffa500;
            --kg-accent: #ffa500;
            box-shadow: 0 0 0 2px rgba(255, 165, 0, 0.45);
        }
        .kg-node__label {
            pointer-events: none;
            white-space: normal;
            overflow-wrap: anywhere;
            word-break: break-word;
        }
        :host ::ng-deep .f-connection path {
            stroke: #d3d3d3;
            stroke-width: 2px;
        }
    `],
})
export class FoblexGraphComponent {
    store = inject(GraphStore);
    private layoutService = inject(GraphLayoutService);

    private flow = viewChild(FFlowComponent);
    private canvas = viewChild(FCanvasComponent);
    private nodeMenu = viewChild<ContextMenu>('nodeMenu');
    private canvasMenu = viewChild<ContextMenu>('canvasMenu');

    selectedId = computed(() => this.store.selectedNodeKey());

    /** Positions owned by this renderer, produced by the ELK layout. */
    private positions = signal(new Map<string, NodePosition>());

    private renderNodes = computed(() => {
        const graph = this.store.filteredGraph();
        const weightNodes = this.store.weightNodes();
        const degreeMap = this.store.degreeMap();
        const maxDegree = this.store.maxDegree() || 1;
        return graph.nodes.map((n) => {
            // Weighting only widens the layout footprint (more breathing room for
            // hub nodes); the rendered node always sizes itself to its full text.
            const weight = Math.max(degreeMap.get(n.id) || 5, 5) / maxDegree; // 0..1
            const scale = weightNodes ? 1 + weight : 1;
            return {
                id: n.id,
                name: this.store.getNodeName(n),
                color: this.store.getNodeColor(n),
                width: Math.round(150 * scale),
                height: Math.round(56 * scale),
            };
        });
    });

    renderEdges = computed(() => {
        const graph = this.store.filteredGraph();
        return graph.edges.map((e, i) => ({
            id: `${e.source}__${e.target}__${i}`,
            source: e.source,
            target: e.target,
        }));
    });

    displayNodes = computed(() => {
        const pos = this.positions();
        return this.renderNodes().map((n) => ({
            ...n,
            position: pos.get(n.id) ?? { x: 0, y: 0 },
        }));
    });

    private layoutSeq = 0;

    constructor() {
        // Recompute the ELK layout whenever the graph, weighting or repulsion changes.
        effect(() => {
            const nodes = this.renderNodes();
            const edges = this.renderEdges();
            const algorithm = this.store.graphLayoutAlgorithm();
            const repulsion = this.store.nodeRepulsion();
            untracked(() => this.recomputeLayout(nodes, edges, algorithm, repulsion));
        });

        // Mirror cytoscape's plot-mode centering: focus + zoom the selected node.
        effect(() => {
            const selection = this.store.selectedNode();
            const plotMode = this.store.showPlot();
            const canvas = this.canvas();
            if (canvas && selection && plotMode) {
                untracked(() => {
                    canvas.setScale(3);
                    canvas.centerGroupOrNode(selection.id, true);
                    this.flow()?.select([selection.id], []);
                });
            }
        });

        // Keep the graph fitted when the plot splitter resizes.
        this.store.plotResize.pipe(takeUntilDestroyed()).subscribe(() => {
            this.canvas()?.fitToScreen(undefined, false);
        });
    }

    private async recomputeLayout(
        nodes: { id: string; width: number; height: number }[],
        edges: { source: string; target: string }[],
        algorithm: GraphLayoutAlgorithm,
        repulsion: number,
    ): Promise<void> {
        const seq = ++this.layoutSeq;
        const map = await this.layoutService.layout(
            nodes.map((n) => ({ id: n.id, width: n.width, height: n.height })),
            edges,
            algorithm,
            repulsion,
        );
        if (seq !== this.layoutSeq) {
            return; // a newer layout superseded this one
        }
        this.positions.set(map);
        // Let the nodes render at their new positions, then frame them.
        setTimeout(() => this.canvas()?.fitToScreen(undefined, false));
    }

    onRendered(): void {
        this.canvas()?.fitToScreen(undefined, false);
    }

    onNodeMoved(id: string, position: NodePosition): void {
        // Persist manual drags so the next change detection doesn't snap them back.
        this.positions.update((prev) => {
            const next = new Map(prev);
            next.set(id, position);
            return next;
        });
    }

    onNodeClick(id: string): void {
        this.store.selectedNodeKey.set(id);
    }

    onNodeContext(event: MouseEvent, id: string): void {
        event.preventDefault();
        event.stopPropagation();
        this.store.selectedNodeKey.set(id);
        this.nodeMenu()?.show(event);
    }

    onCanvasContext(event: MouseEvent): void {
        // Node right-clicks call stopPropagation, so reaching here means the
        // background (or a connection) was the target.
        event.preventDefault();
        this.store.selectedNodeKey.set('');
        this.canvasMenu()?.show(event);
    }
}
