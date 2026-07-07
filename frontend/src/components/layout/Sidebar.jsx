import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { FolderKanban, Settings, LogOut, BookOpen, PieChart, Zap } from 'lucide-react';
import { motion } from 'framer-motion';
import { useAuth } from '../../context/AuthContext';

const NAV_ITEMS = [
  { name: 'Projects',       icon: FolderKanban, path: '/projects' },
  { name: 'Knowledge Base', icon: BookOpen,      path: '/knowledge' },
  { name: 'Analytics',      icon: PieChart,      path: '/analytics' },
  { name: 'Settings',       icon: Settings,      path: '/settings' },
];

const Sidebar = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <motion.aside
      initial={{ x: -260, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.35, ease: 'easeOut' }}
      className="
        w-64 shrink-0 h-screen sticky top-0 flex flex-col
        bg-black/40 backdrop-blur-2xl
        border-r border-white/8
      "
    >
      {/* Logo */}
      <div className="flex items-center gap-3 px-6 py-5 border-b border-white/8">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-violet-500 to-purple-700 flex items-center justify-center text-white font-bold text-lg shadow-[0_0_16px_rgba(139,92,246,0.55)] shrink-0">
          E
        </div>
        <div>
          <span className="text-base font-bold text-gradient block leading-tight">EduDeck AI</span>
          <span className="text-[10px] text-muted-foreground tracking-widest uppercase">Pro Workspace</span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.name}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${
                isActive
                  ? 'bg-primary/15 text-primary border border-primary/20 shadow-[inset_0_0_15px_rgba(139,92,246,0.1)]'
                  : 'text-muted-foreground hover:text-foreground hover:bg-white/6'
              }`
            }
          >
            {({ isActive }) => (
              <>
                <item.icon size={17} className={isActive ? 'text-primary' : ''} />
                {item.name}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* User Panel */}
      <div className="px-3 pb-4 space-y-2 border-t border-white/8 pt-4">
        {user && (
          <div className="rounded-xl bg-white/4 border border-white/8 p-3 space-y-3">
            {/* Avatar + info */}
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-full bg-primary/20 border border-primary/30 flex items-center justify-center text-primary font-bold text-sm shrink-0">
                {(user.name || user.email).charAt(0).toUpperCase()}
              </div>
              <div className="overflow-hidden flex-1 min-w-0">
                <p className="text-sm font-semibold text-foreground truncate">{user.name || 'User'}</p>
                <p className="text-xs text-muted-foreground truncate">{user.email}</p>
              </div>
            </div>

            {/* Credits */}
            <div className="flex items-center justify-between bg-black/30 rounded-lg px-3 py-2 border border-white/6">
              <div className="flex items-center gap-1.5 text-muted-foreground text-xs font-medium">
                <Zap size={12} className="text-primary" />
                Credits
              </div>
              <span className="text-sm font-bold text-primary">{user.credits?.toLocaleString() ?? '—'}</span>
            </div>

            {/* Buy credits */}
            <button
              className="w-full py-2 rounded-lg bg-primary/10 border border-primary/20 text-primary text-xs font-semibold
                         hover:bg-primary/20 transition-all duration-200 cursor-not-allowed opacity-70"
              title="Coming soon"
            >
              Buy Credits
            </button>
          </div>
        )}

        {/* Logout */}
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 w-full px-3 py-2.5 rounded-xl text-sm font-medium text-muted-foreground
                     hover:text-red-400 hover:bg-red-500/8 transition-all duration-200"
        >
          <LogOut size={17} />
          Log out
        </button>
      </div>
    </motion.aside>
  );
};

export default Sidebar;
