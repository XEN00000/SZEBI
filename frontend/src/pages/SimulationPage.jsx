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
        <div className="acquisition-container">
            <div className="acquisition-content">
                <div className="header-section">
                    <h1 className="page-title">Simulation Module</h1>
                    <p className="page-subtitle">Managing virtual devices and test scenarios</p>

                    <DashboardSimulation refreshKey={refreshKey} />
                </div>

                <div className="manager-section">
                    <SimulationManager onSimulationRun={handleSimulationRun} />
                </div>

                <div className="history-section">
                    <SimulationHistory key={refreshKey} />
                </div>
            </div>
        </div>
    );
};

export default SimulationPage;