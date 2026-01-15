import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import Home from './pages/Home';
import LoginPage from './pages/LoginPage';

// Definicje ról zgodne z core/models.py
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
            <Route path="simulation" element={<div className="p-8 text-center text-gray-400">Moduł Symulacji Środowiska</div>} />
          </Route>

          <Route element={<ProtectedRoute user={user} allowedRoles={[ROLES.ADMIN, ROLES.MAINTENANCE]} />}>
            <Route path="acquisition" element={<div className="p-8 text-center text-gray-400">Moduł Akwizycji Danych</div>} />
            <Route path="analysis" element={<div className="p-8 text-center text-gray-400">Moduł Analizy i Raportowania</div>} />
            <Route path="forecasting" element={<div className="p-8 text-center text-gray-400">Moduł Prognozowania</div>} />
            <Route path="alarms" element={<div className="p-8 text-center text-gray-400">Moduł Alarmów i Utrzymania</div>} />
          </Route>

          <Route element={<ProtectedRoute user={user} allowedRoles={[ROLES.ADMIN, ROLES.MAINTENANCE, ROLES.WORKER]} />}>
            <Route path="optimization" element={<div className="p-8 text-center text-gray-400">Moduł Optymalizacji i Sterowania</div>} />
          </Route>

          <Route path="*" element={<div className="p-8 text-center text-gray-400">404 - Strona nie odnaleziona</div>} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;