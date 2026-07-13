import { Activity as ActivityIcon, Clock, Terminal } from 'lucide-react';

export default function Activity() {
  const logs = [
    { time: '10:45 AM', action: 'Layer 1: Intent Analyzer', detail: 'Classified intent as "get_system_stats"' },
    { time: '10:45 AM', action: 'Layer 3: Tool Executor', detail: 'Executed tool "get_system_stats" successfully' },
    { time: '10:46 AM', action: 'Layer 5: Response', detail: 'Generated natural language response to user' },
    { time: '10:47 AM', action: 'Layer 0: Classifier', detail: 'Identified request as Web Task' },
  ];

  return (
    <div className="p-10 text-white max-w-5xl mx-auto w-full">
      <div className="flex items-center space-x-3 mb-8">
        <ActivityIcon className="w-8 h-8 text-blue-500" />
        <h1 className="text-3xl font-bold tracking-tight">Agent Activity</h1>
      </div>
      
      <div className="relative border-l border-zinc-800 ml-4 space-y-8 pb-10">
        {logs.map((log, i) => (
          <div key={i} className="relative pl-8 group">
            <div className="absolute -left-[5px] top-1.5 w-2.5 h-2.5 rounded-full bg-blue-500 ring-4 ring-zinc-950 group-hover:scale-125 transition-transform" />
            <div className="bg-zinc-900/40 backdrop-blur-md border border-zinc-800/80 rounded-2xl p-5 hover:bg-zinc-900/60 transition-colors">
              <div className="flex items-center space-x-2 text-xs text-zinc-500 mb-2 font-mono">
                <Clock className="w-3.5 h-3.5" />
                <span>{log.time}</span>
              </div>
              <div className="flex items-center space-x-2 mb-1.5">
                <Terminal className="w-4 h-4 text-zinc-400" />
                <h3 className="text-sm font-bold text-zinc-200 uppercase tracking-wider">{log.action}</h3>
              </div>
              <p className="text-zinc-400 text-sm">{log.detail}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
