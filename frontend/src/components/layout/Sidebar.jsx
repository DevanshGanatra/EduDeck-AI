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

const Sidebar = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('token');
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
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-500 to-brand-700 flex items-center justify-center text-white font-bold text-xl shadow-md">
            E
          </div>
          <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-gray-900 to-gray-600">
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
                    ? 'bg-brand-50 text-brand-700 font-medium shadow-sm border border-brand-100/50'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }`
              }
            >
              <item.icon size={20} className="shrink-0" />
              {item.name}
            </NavLink>
          ))}
        </nav>
      </div>

      <button
        onClick={handleLogout}
        className="flex items-center gap-3 px-4 py-3 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-xl transition-colors w-full text-left"
      >
        <LogOut size={20} className="shrink-0" />
        <span className="font-medium">Logout</span>
      </button>
    </motion.aside>
  );
};

export default Sidebar;
