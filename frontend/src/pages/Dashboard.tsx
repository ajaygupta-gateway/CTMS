import { useEffect, useState } from 'react';
import { tasksApi } from '../api/tasks';
import type { AnalyticsData } from '../types';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Activity, Users, CheckCircle } from 'lucide-react';
import KanbanBoard from '../components/KanbanBoard';
import DependencyGraph from '../components/DependencyGraph';

export default function Dashboard() {
    const [data, setData] = useState<AnalyticsData | null>(null);

    useEffect(() => {
        tasksApi.getAnalytics().then((res) => setData(res.data)).catch(console.error);
    }, []);

    if (!data) return <div>Loading dashboard...</div>;

    return (
        <div className="space-y-6">
            <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>

            <div className="grid gap-4 md:grid-cols-3">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">My Tasks</CardTitle>
                        <CheckCircle className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{data.my_tasks.total}</div>
                        <p className="text-xs text-muted-foreground">
                            {data.my_tasks.completed} completed, {data.my_tasks.pending} pending
                        </p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Team Tasks</CardTitle>
                        <Users className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{data.team_tasks.total}</div>
                        <p className="text-xs text-muted-foreground">
                            {data.team_tasks.completed} completed
                        </p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Efficiency Score</CardTitle>
                        <Activity className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{data.efficiency_score}%</div>
                        <p className="text-xs text-muted-foreground">
                            Overall performance
                        </p>
                    </CardContent>
                </Card>
            </div>

            <div className="grid grid-cols-1 gap-8">
                <KanbanBoard />
                <DependencyGraph />
            </div>
        </div>
    );
}
