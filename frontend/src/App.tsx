import { Routes, Route, useLocation } from 'react-router-dom';
// Layout
import Sidebar from './components/layout/Sidebar';
// Pages
import Home from './pages/Home';
import Settings from './pages/Settings';
import Memory from './pages/Memory';
import Activity from './pages/Activity';
import StandaloneConfirm from './pages/StandaloneConfirm';
import { Toaster } from 'react-hot-toast';
function App() {
  const location = useLocation();

  // If we are in the standalone confirmation window, hide the standard layout
  if (location.hash.includes('#/confirm')) {
    return <StandaloneConfirm />;
  }

  return (
    <div className="flex h-screen w-screen bg-background text-foreground overflow-hidden">
      {/* Sidebar Navigation */}
      <Sidebar />
      <Toaster position="top-right" toastOptions={{ className: 'bg-zinc-900 text-white border border-zinc-800' }} />
      
      {/* Main Content Area */}
      <main className="flex-1 flex flex-col h-full relative">
        {/* Titlebar drag region for frameless Electron window */}
        <div className="h-8 w-full app-region-drag absolute top-0 left-0 z-50"></div>
        
        <div className="flex-1 mt-8 overflow-y-auto">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/memory" element={<Memory />} />
            <Route path="/activity" element={<Activity />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </div>
      </main>
    </div>
  );
}

export default App;
