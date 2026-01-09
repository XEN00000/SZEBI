import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Home from './pages/Home';
import LoginPage from './pages/LoginPage';

function App() {
  const [user, setUser] = useState(null);

  if (!user) {
    return <LoginPage onLoginSuccess={(userData) => setUser(userData)} />;
  }

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout user={user} />}>
          <Route index element={<Home />} />
          {user.is_admin && (
            <Route path="simulation" element={<div className="p-8 text-center text-gray-400">Moduł Symulacji Środowiska</div>} />
          )}
          
          <Route path="acquisition" element={<div className="p-8 text-center text-gray-400">Moduł Akwizycji Danych</div>} />
          <Route path="analysis" element={<div className="p-8 text-center text-gray-400">Moduł Analizy i Raportowania</div>} />
          <Route path="forecasting" element={<div className="p-8 text-center text-gray-400">Moduł Prognozowania</div>} />
          <Route path="optimization" element={<div className="p-8 text-center text-gray-400">Moduł Optymalizacji i Sterowania</div>} />
          <Route path="alarms" element={<div className="p-8 text-center text-gray-400">Moduł Alarmów i Utrzymania</div>} />
          
          <Route path="*" element={<div className="p-8 text-center text-gray-400">404 - Strona nie odnaleziona</div>} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;