import { Database, Search, Sparkles } from 'lucide-react';

export default function Memory() {
  const memories = [
    { type: 'Preference', content: 'Prefers dark mode' },
    { type: 'Fact', content: 'Works on the EZIO Desktop Assistant project' },
    { type: 'Context', content: 'Located in C:\\Users\\KIIT0001\\Desktop\\Antigravity\\AI_Assistant' },
  ];

  return (
    <div className="p-10 text-white max-w-5xl mx-auto w-full">
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center space-x-3">
          <Database className="w-8 h-8 text-blue-500" />
          <h1 className="text-3xl font-bold tracking-tight">Memory Browser</h1>
        </div>
        <div className="relative">
          <Search className="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" />
          <input
            type="text"
            placeholder="Search memories..."
            className="bg-zinc-900/50 backdrop-blur-xl border border-zinc-800 rounded-xl py-2 pl-10 pr-4 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all w-64"
          />
        </div>
      </div>
      
      <div className="space-y-4">
        {memories.map((m, i) => (
          <div key={i} className="flex items-center space-x-4 bg-zinc-900/40 backdrop-blur-md border border-zinc-800/80 rounded-2xl p-5 hover:bg-zinc-900/60 transition-all group">
            <div className="p-2.5 bg-blue-500/10 text-blue-400 rounded-xl">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <span className="text-xs font-bold text-zinc-500 uppercase tracking-wider">{m.type}</span>
              <p className="text-zinc-200 mt-1">{m.content}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
