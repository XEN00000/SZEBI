
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Home from './pages/Home';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="optimization" element={<div className="p-8 text-center text-gray-400">Optimization Module Placeholder</div>} />
          <Route path="alarms" element={<div className="p-8 text-center text-gray-400">Alarms Module Placeholder</div>} />
          <Route path="analysis" element={<div className="p-8 text-center text-gray-400">Analysis Module Placeholder</div>} />
          <Route path="*" element={<div className="p-8 text-center text-gray-400">404 - Not Found</div>} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
