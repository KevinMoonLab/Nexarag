import { inject, Injectable } from '@angular/core';
import { IFLayoutConnection, IFLayoutNode } from '@foblex/flow';
import { EElkLayoutAlgorithm, ElkLayoutEngine } from '@foblex/flow-elk-layout';

/** The subset of ELK algorithms exposed to the user as layout choices. */
export type GraphLayoutAlgorithm = 'force' | 'stress' | 'radial' | 'layered' | 'mrtree';

const ALGORITHM_MAP: Record<GraphLayoutAlgorithm, EElkLayoutAlgorithm> = {
    force: EElkLayoutAlgorithm.FORCE,
    stress: EElkLayoutAlgorithm.STRESS,
    radial: EElkLayoutAlgorithm.RADIAL,
    layered: EElkLayoutAlgorithm.LAYERED,
    mrtree: EElkLayoutAlgorithm.MRTREE,
};

export interface LayoutNode {
    id: string;
    /** Node footprint in px; feeds ELK's collision spacing. */
    width: number;
    height: number;
}

export interface LayoutEdge {
    source: string;
    target: string;
}

export interface NodePosition {
    x: number;
    y: number;
}

/**
 * Wraps Foblex's ELK layout engine to reproduce the force-directed arrangement
 * that the cytoscape renderer gets from `cose-bilkent`. The Foblex renderer owns
 * its node positions, so this service is a pure transform: graph in, positions
 * out. The engine itself is registered per-component via `provideFLayout`.
 */
@Injectable()
export class GraphLayoutService {
    private readonly engine = inject(ElkLayoutEngine);

    /**
     * @param algorithm which ELK layout to run.
     * @param repulsion mirrors the store's `nodeRepulsion` signal (default 9);
     *   higher values spread nodes further apart.
     */
    async layout(
        nodes: LayoutNode[],
        edges: LayoutEdge[],
        algorithm: GraphLayoutAlgorithm,
        repulsion: number,
    ): Promise<Map<string, NodePosition>> {
        const positions = new Map<string, NodePosition>();
        if (!nodes.length) {
            return positions;
        }

        const layoutNodes: IFLayoutNode[] = nodes.map((n) => ({
            id: n.id,
            size: { width: n.width, height: n.height },
        }));
        const layoutConnections: IFLayoutConnection[] = edges.map((e) => ({
            source: e.source,
            target: e.target,
        }));

        // Tight by default; `repulsion` nudges nodes apart a little.
        const spacing = Math.max(8, repulsion * 3);
        const result = await this.engine.calculate(layoutNodes, layoutConnections, {
            algorithm: ALGORITHM_MAP[algorithm],
            nodeGap: spacing,
            defaultNodeSize: { width: 50, height: 50 },
            layoutOptions: {
                'elk.spacing.nodeNode': `${spacing}`,
                'elk.force.repulsivePower': '1',
            },
        });

        for (const node of result.nodes) {
            positions.set(node.id, { x: node.position.x, y: node.position.y });
        }
        return positions;
    }
}
