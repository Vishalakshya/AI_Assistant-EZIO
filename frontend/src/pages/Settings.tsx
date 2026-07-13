import { Settings as SettingsIcon, Shield, Sliders, HardDrive, Bot } from 'lucide-react';

export default function Settings() {
  const sections = [
    { title: 'General', icon: Sliders, description: 'Basic application settings' },
    { title: 'AI Model', icon: Bot, description: 'Ollama model configuration' },
    { title: 'Security & Permissions', icon: Shield, description: 'Manage Tier 3 approvals' },
    { title: 'Storage & Memory', icon: HardDrive, description: 'Manage SQLite databases' },
  ];

  return (
    <div className="p-10 text-white max-w-5xl mx-auto w-full">
      <div className="flex items-center space-x-3 mb-8">
        <SettingsIcon className="w-8 h-8 text-blue-500" />
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {sections.map((section) => (
          <div key={section.title} className="bg-zinc-900/40 backdrop-blur-md border border-zinc-800/80 rounded-2xl p-6 hover:bg-zinc-900/60 transition-colors cursor-pointer group">
            <div className="flex items-center space-x-4">
              <div className="p-3 bg-zinc-800/50 rounded-xl group-hover:bg-blue-500/10 group-hover:text-blue-400 transition-colors">
                <section.icon className="w-6 h-6" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-zinc-100">{section.title}</h3>
                <p className="text-sm text-zinc-400 mt-1">{section.description}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
