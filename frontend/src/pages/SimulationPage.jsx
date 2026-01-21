import React, { useState } from 'react';
import DashboardSimulation from '../components/simulation/DashboardSimulation';
import SimulationHistory from '../components/simulation/SimulationHistory';
import SimulationManager from '../components/simulation/SimulationManager';

const SimulationPage = () => {
    const [refreshKey, setRefreshKey] = useState(0);

    const handleSimulationRun = () => {
        setRefreshKey(k => k + 1);
    };

    return (
        <div className="container mx-auto py-6">
            <h1 className="text-2xl font-bold mb-4">Moduł symulacji</h1>
            <DashboardSimulation refreshKey={refreshKey} />
            <SimulationManager onSimulationRun={handleSimulationRun} />
            <SimulationHistory key={refreshKey} />
        </div>
    );
};

export default SimulationPage;
