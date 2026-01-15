import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';

const ProtectedRoute = ({ user, allowedRoles, children }) => {
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  const userRole = user.role; 

  if (allowedRoles && !allowedRoles.includes(userRole)) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center p-8 bg-gray-800 rounded-lg border border-gray-700">
          <h2 className="text-xl text-red-500 mb-2">Brak uprawnień</h2>
          <p className="text-gray-400">Twoja rola ({userRole}) nie ma dostępu do tego modułu.</p>
        </div>
      </div>
    );
  }

  return children ? children : <Outlet />;
};

export default ProtectedRoute;