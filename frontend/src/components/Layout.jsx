import React, { useState } from 'react';
import { Link, Outlet, useLocation } from 'react-router-dom';
import { Menu, X, Rocket, Zap, BarChart, Database, TrendingUp, Play } from 'lucide-react';

const Layout = ({ user }) => {
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const location = useLocation();

    const navItems = [
        { name: 'Optimization', path: '/optimization', icon: Rocket, adminOnly: false },
        { name: 'Alarms', path: '/alarms', icon: Zap, adminOnly: false },
        { name: 'Analysis', path: '/analysis', icon: BarChart, adminOnly: false },
        { name: 'Acquisition', path: '/acquisition', icon: Database, adminOnly: false },
        { name: 'Forecasting', path: '/forecasting', icon: TrendingUp, adminOnly: false },
        { name: 'Simulation', path: '/simulation', icon: Play, adminOnly: true },
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
                        
                        <div className="hidden md:flex items-center ml-4 px-3 py-1 bg-gray-800 rounded-full text-[10px] text-gray-400">
                            Użytkownik: <span className="text-emerald-400 ml-1 font-mono">{user?.username}</span>
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
                            if (item.adminOnly && !user?.is_admin) return null;

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