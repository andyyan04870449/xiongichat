import { useState } from 'react';
import { ChatPaper } from './components/ChatPaper';
import { StickyNotes } from './components/StickyNotes';

export default function App() {
  const [activeFunction, setActiveFunction] = useState<string | null>(null);

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-red-50 relative overflow-hidden">
      {/* Desktop Background Texture */}
      <div className="fixed inset-0 opacity-30">
        <div className="absolute inset-0 bg-gradient-to-r from-yellow-100/20 to-orange-100/20"></div>
        <div 
          className="absolute inset-0" 
          style={{
            backgroundImage: `
              radial-gradient(circle at 20% 30%, rgba(255,200,100,0.1) 1px, transparent 1px),
              radial-gradient(circle at 80% 70%, rgba(255,150,150,0.1) 1px, transparent 1px),
              radial-gradient(circle at 40% 80%, rgba(100,200,255,0.1) 1px, transparent 1px)
            `,
            backgroundSize: '100px 100px, 150px 150px, 120px 120px'
          }}
        ></div>
      </div>

      {/* Wood grain texture overlay */}
      <div 
        className="fixed inset-0 opacity-10"
        style={{
          backgroundImage: `
            linear-gradient(90deg, rgba(139,69,19,0.1) 0%, transparent 2%, transparent 98%, rgba(139,69,19,0.1) 100%),
            linear-gradient(0deg, rgba(160,82,45,0.05) 0%, transparent 1%, transparent 99%, rgba(160,82,45,0.05) 100%)
          `,
          backgroundSize: '20px 20px, 15px 15px'
        }}
      ></div>

      {/* Main Layout Container */}
      <div className="flex h-screen">
        {/* Left Side - Chat Area */}
        <div className="flex-1 p-4">
          <ChatPaper />
        </div>

        {/* Right Side - Function Services */}
        <div className="w-80 p-4">
          <StickyNotes 
            activeFunction={activeFunction} 
            onFunctionClick={setActiveFunction} 
          />
        </div>
      </div>



      {/* Coffee stain decoration */}
      <div className="fixed bottom-20 right-20 w-16 h-16 bg-amber-800/20 rounded-full blur-sm opacity-50"></div>
      <div className="fixed top-32 right-32 w-8 h-8 bg-amber-700/15 rounded-full blur-sm opacity-40"></div>
    </div>
  );
}