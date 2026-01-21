import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import Home from './pages/Home';
import AlarmsPage from './pages/AlarmsPage';
import LoginPage from './pages/LoginPage';
import AnalysisDashboard from './pages/AnalysisDashboard.jsx';
import AcquisitionPage from './pages/AcquisitionPage';
import Forecasting from "./pages/Forecasting.jsx";
import OptimalizationPage from './pages/OptimalizationPage';
import SimulationPage from './pages/SimulationPage';

const ROLES = {
  ADMIN: 'building_admin',
  WORKER: 'worker',
  MAINTENANCE: 'maintenance_engineer',
  PROVIDER: 'energy_provider'
};

function App() {
  const [user, setUser] = useState(null);

  const handleLogout = () => {
    setUser(null);
  };

  if (!user) {
    return <LoginPage onLoginSuccess={(userData) => setUser(userData)} />;
  }

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout user={user} onLogout={handleLogout} />}>
          <Route index element={<Home />} />

          <Route element={<ProtectedRoute user={user} allowedRoles={[ROLES.ADMIN, ROLES.PROVIDER]} />}>
            <Route path="simulation" element={<SimulationPage />} />
          </Route>

          <Route element={<ProtectedRoute user={user} allowedRoles={[ROLES.ADMIN, ROLES.MAINTENANCE]} />}>
            <Route path="acquisition" element={<AcquisitionPage />} />
            <Route path="analysis" element={<AnalysisDashboard />} />
            <Route path="forecasting" element={<Forecasting user={user} />} />
            <Route path="alarms" element={<AlarmsPage />} />
          </Route>

          <Route element={<ProtectedRoute user={user} allowedRoles={[ROLES.ADMIN, ROLES.MAINTENANCE, ROLES.WORKER]} />}>
            <Route path="optimization" element={<OptimalizationPage userRole={user?.role} userId={user?.id} />} />
          </Route>

          <Route path="*" element={<div className="p-8 text-center text-gray-400">404 - Strona nie odnaleziona</div>} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;