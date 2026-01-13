import { useState, useEffect } from 'react';
import ReactFlow, {
    Background,
    Controls,
    MarkerType,
    useNodesState,
    useEdgesState,
    ReactFlowProvider
} from 'reactflow';
import type { Node, Edge } from 'reactflow';
import 'reactflow/dist/style.css';
import { tasksApi } from '../api/tasks';
import type { Task } from '../types';

const GraphContent = ({ initialTasks }: { initialTasks?: Task[] }) => {
    const [tasks, setTasks] = useState<Task[]>([]);
    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);

    useEffect(() => {
        // If initialTasks provided, use them
        if (initialTasks && initialTasks.length > 0) {
            setTasks(initialTasks);
        } else if (!initialTasks) {
            // Otherwise fetch from API
            const loadTasks = async () => {
                try {
                    const response = await tasksApi.getTasks();
                    setTasks(response.data);
                } catch (error) {
                    console.error("Failed to load tasks for graph", error);
                }
            };
            loadTasks();
        }
    }, [initialTasks]);

    useEffect(() => {
        if (tasks.length === 0) return;

        // Transform Tasks to Nodes/Edges with Layout
        const newNodes: Node[] = [];
        const newEdges: Edge[] = [];

        // Simple Layout Algorithm
        // 1. Identify levels
        // 2. Position nodes

        const levels: Record<number, number> = {}; // taskId -> level
        const getLevel = (taskId: number): number => {
            if (taskId in levels) return levels[taskId];
            const task = tasks.find(t => t.id === taskId);
            // Safety check for circular deps or missing parents
            if (!task || !task.parent_task) {
                levels[taskId] = 0;
                return 0;
            }
            // Recursive level finding (with basic loop protection could be added, assuming standard tree)
            const parentLevel = getLevel(task.parent_task);
            levels[taskId] = parentLevel + 1;
            return parentLevel + 1;
        };

        // Calculate levels
        tasks.forEach(task => getLevel(task.id));

        // Group by level for X positioning
        const levelGroups: Record<number, Task[]> = {};
        tasks.forEach(task => {
            const lvl = levels[task.id];
            if (!levelGroups[lvl]) levelGroups[lvl] = [];
            levelGroups[lvl].push(task);
        });

        // Create Nodes
        Object.entries(levelGroups).forEach(([lvlStr, levelTasks]) => {
            const level = Number(lvlStr);
            levelTasks.forEach((task, index) => {
                newNodes.push({
                    id: task.id.toString(),
                    data: { label: task.title },
                    position: { x: index * 250, y: level * 150 },
                    style: {
                        background: '#fff',
                        border: '1px solid #777',
                        padding: '10px',
                        borderRadius: '5px',
                        width: 200,
                        fontSize: '12px'
                    }
                });

                if (task.parent_task) {
                    newEdges.push({
                        id: `e${task.parent_task}-${task.id}`,
                        source: task.parent_task.toString(),
                        target: task.id.toString(),
                        markerEnd: { type: MarkerType.ArrowClosed },
                        type: 'smoothstep'
                    });
                }
            });
        });

        setNodes(newNodes);
        setEdges(newEdges);

    }, [tasks, setNodes, setEdges]);

    return (
        <div style={{ height: 500, width: '100%' }} className="border rounded-lg bg-slate-50">
            <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                fitView
            >
                <Background />
                <Controls />
            </ReactFlow>
        </div>
    );
};

export default function DependencyGraph({ initialTasks }: { initialTasks?: Task[] }) {
    return (
        <div className="space-y-4">
            <h2 className="text-2xl font-bold">Task Dependency Graph</h2>
            <ReactFlowProvider>
                <GraphContent initialTasks={initialTasks} />
            </ReactFlowProvider>
        </div>
    );
}
