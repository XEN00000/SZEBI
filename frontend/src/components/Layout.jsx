import React, { useState } from 'react';
import { Link, Outlet, useLocation } from 'react-router-dom';
import { Menu, X, Rocket, Zap, BarChart, Database, TrendingUp, Play, LogOut } from 'lucide-react';

const ROLES = {
  ADMIN: 'building_admin',
  WORKER: 'worker',
  MAINTENANCE: 'maintenance_engineer',
  PROVIDER: 'energy_provider'
};

const Layout = ({ user, onLogout }) => {
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const location = useLocation();

    const navItems = [
        { 
            name: 'Optimization', 
            path: '/optimization', 
            icon: Rocket, 
            allowedRoles: [ROLES.ADMIN, ROLES.MAINTENANCE, ROLES.WORKER] 
        },
        { 
            name: 'Alarms', 
            path: '/alarms', 
            icon: Zap, 
            allowedRoles: [ROLES.ADMIN, ROLES.MAINTENANCE] 
        },
        { 
            name: 'Analysis', 
            path: '/analysis', 
            icon: BarChart, 
            allowedRoles: [ROLES.ADMIN, ROLES.MAINTENANCE] 
        },
        { 
            name: 'Acquisition', 
            path: '/acquisition', 
            icon: Database, 
            allowedRoles: [ROLES.ADMIN, ROLES.MAINTENANCE] 
        },
        { 
            name: 'Forecasting', 
            path: '/forecasting', 
            icon: TrendingUp, 
            allowedRoles: [ROLES.ADMIN, ROLES.MAINTENANCE] 
        },
        { 
            name: 'Simulation', 
            path: '/simulation', 
            icon: Play, 
            allowedRoles: [ROLES.ADMIN, ROLES.PROVIDER] 
        },
    ];

    const isActive = (path) => location.pathname.startsWith(path);

    return (
        <div className="app-container">
            <nav className="navbar">
                <div className="nav-content">
                    <div className="nav-header">
                        <Link to="/" className="logo-container">
                            <div className="logo-icon"><span>S</span></div>
                            <span className="logo-text">SZEBI</span>
                        </Link>
                        
                        <div className="hidden md:flex items-center ml-4 gap-2">
                            <div className="px-3 py-1 bg-gray-800 rounded-full text-[10px] text-gray-400">
                                Użytkownik: <span className="text-emerald-400 ml-1 font-mono">{user?.username} ({user?.role})</span>
                            </div>
                        </div>

                        <button
                            onClick={() => setIsMenuOpen(!isMenuOpen)}
                            className="mobile-menu-btn"
                        >
                            {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
                        </button>
                    </div>

                    <div className={`nav-links ${isMenuOpen ? 'open' : ''}`}>
                        {navItems.map((item) => {
                            if (!user || !item.allowedRoles.includes(user.role)) return null;

                            const Icon = item.icon;
                            return (
                                <Link
                                    key={item.name}
                                    to={item.path}
                                    className={`nav-item ${isActive(item.path) ? 'active' : ''}`}
                                    onClick={() => setIsMenuOpen(false)}
                                >
                                    <Icon size={18} />
                                    <span>{item.name}</span>
                                </Link>
                            );
                        })}
                        
                        <button 
                            onClick={() => {
                                setIsMenuOpen(false);
                                onLogout();
                            }}
                            className="flex items-center gap-2 text-red-400 hover:text-red-300 transition-colors mt-2 md:mt-0 md:ml-6"
                        >
                            <LogOut size={16} />
                            <span>Wyloguj się</span>
                        </button>
                    </div>
                </div>
            </nav>
            
            <main className="main-content">
                <div className="content-wrapper">
                    <Outlet />
                </div>
            </main>

            <footer className="footer">
                <div className="footer-content">
                    <div className="footer-left">
                        © 2026 SZEBI Project. System Zarządzania Energią Budynków Inteligentnych.
                    </div>
                </div>
            </footer>
        </div>
    );
};

export default Layout;