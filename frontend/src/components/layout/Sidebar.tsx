import { NavLink } from 'react-router-dom';
import { MessageSquare, Settings, Activity, Database, Zap } from 'lucide-react';

export default function Sidebar() {
  const navItems = [
    { name: 'Chat', path: '/', icon: MessageSquare },
    { name: 'Memory', path: '/memory', icon: Database },
    { name: 'Activity', path: '/activity', icon: Activity },
    { name: 'Settings', path: '/settings', icon: Settings },
  ];

  return (
    <div className="w-[280px] bg-zinc-950/80 backdrop-blur-3xl border-r border-zinc-800/50 flex flex-col pt-12 relative z-40 shadow-2xl">
      <div className="px-8 pb-8 flex items-center space-x-3">
        <div className="w-10 h-10 bg-gradient-to-tr from-blue-600 to-cyan-400 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/20">
          <Zap className="w-6 h-6 text-white" />
        </div>
        <div className="font-bold text-2xl tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-zinc-100 to-zinc-400">EZIO</div>
      </div>
      
      <nav className="flex flex-col gap-2 px-4 flex-1">
        {navItems.map((item) => (
          <NavLink
            key={item.name}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-200 ${
                isActive
                  ? 'bg-blue-600/10 text-blue-400 font-medium'
                  : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50'
              }`
            }
          >
            <item.icon className="w-5 h-5" strokeWidth={2} />
            <span className="text-[15px]">{item.name}</span>
          </NavLink>
        ))}
      </nav>
      
      <div className="p-6">
        <div className="bg-zinc-900/50 border border-zinc-800 rounded-2xl p-4 flex flex-col space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-zinc-500 uppercase tracking-wider">System Status</span>
            <div className="flex space-x-1">
              <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
            </div>
          </div>
          <span className="text-sm font-medium text-zinc-300">Online & Ready</span>
        </div>
      </div>
    </div>
  );
}
