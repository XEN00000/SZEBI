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
                    <h1 className="page-title">Moduł Symulacji</h1>
                    <p className="page-subtitle">Zarządzanie wirtualnymi urządzeniami i scenariuszami testowymi</p>
                    
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