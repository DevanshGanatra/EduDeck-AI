import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { 
  FolderKanban, 
  Settings, 
  LogOut, 
  BookOpen,
  PieChart
} from 'lucide-react';
import { motion } from 'framer-motion';
import { useAuth } from '../../context/AuthContext';

const Sidebar = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    { name: 'Projects', icon: FolderKanban, path: '/projects' },
    { name: 'Knowledge Base', icon: BookOpen, path: '/knowledge' },
    { name: 'Analytics', icon: PieChart, path: '/analytics' },
    { name: 'Settings', icon: Settings, path: '/settings' },
  ];

  return (
    <motion.aside 
      initial={{ x: -250 }}
      animate={{ x: 0 }}
      className="w-64 h-screen glass-panel flex flex-col justify-between p-4 sticky top-0 m-4 shadow-xl"
    >
      <div>
        <div className="flex items-center gap-3 px-2 mb-8 mt-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-purple-600 flex items-center justify-center text-white font-bold text-xl shadow-[0_0_15px_rgba(139,92,246,0.5)]">
            E
          </div>
          <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
            EduDeck AI
          </span>
        </div>

        <nav className="flex flex-col gap-2">
          {navItems.map((item) => (
            <NavLink
              key={item.name}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 ${
                  isActive
                    ? 'bg-primary/20 text-primary font-medium shadow-sm border border-primary/30'
                    : 'text-muted-foreground hover:bg-white/5 hover:text-foreground'
                }`
              }
            >
              <item.icon size={20} className="shrink-0" />
              {item.name}
            </NavLink>
          ))}
        </nav>
      </div>

      <div className="flex flex-col gap-4">
        {/* User Profile & Credits */}
        {user && (
          <div className="p-4 bg-black/20 rounded-xl border border-white/10 shadow-sm">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center text-primary font-bold border border-primary/30">
                {user.name ? user.name.charAt(0).toUpperCase() : user.email.charAt(0).toUpperCase()}
              </div>
              <div className="overflow-hidden">
                <p className="text-sm font-bold text-foreground truncate">{user.name || 'User'}</p>
                <p className="text-xs text-muted-foreground truncate">{user.email}</p>
              </div>
            </div>
            
            <div className="flex items-center justify-between bg-black/40 rounded-lg p-2 border border-white/5 mb-3">
              <span className="text-xs font-medium text-muted-foreground">Balance</span>
              <span className="text-sm font-bold text-primary flex items-center gap-1">
                <span>⚡</span> {user.credits}
              </span>
            </div>
            
            <button className="w-full py-2 bg-white/10 hover:bg-white/20 text-foreground rounded-lg text-xs font-semibold transition-colors shadow-sm cursor-not-allowed opacity-80" title="Coming Soon">
              Buy Credits
            </button>
          </div>
        )}

        <button
          onClick={handleLogout}
          className="flex items-center gap-3 px-4 py-3 text-muted-foreground hover:text-destructive hover:bg-destructive/10 rounded-xl transition-colors w-full text-left"
        >
          <LogOut size={20} className="shrink-0" />
          <span className="font-medium">Logout</span>
        </button>
      </div>
    </motion.aside>
  );
};

export default Sidebar;
