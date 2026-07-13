import React, { useEffect, useState, useRef } from 'react';
import ChatWindow from '../components/chat/ChatWindow';
import ConfirmationModal from '../components/confirmations/ConfirmationModal';
import { ChatAPI } from '../api/client';
import { useChatStore, ChatMessage } from '../stores/useChatStore';
import { chatSocket, confirmSocket } from '../websocket/client';
import { useConfirmationStore } from '../stores/useConfirmationStore';

const Home: React.FC = () => {
  const [input, setInput] = useState('');
  const addMessage = useChatStore(state => state.addMessage);
  const currentStreamIdRef = useRef<string | null>(null);

  useEffect(() => {
    // 1. Connect WebSockets
    chatSocket.connect();
    confirmSocket.connect();

    // 2. Subscribe to Chat Events (Tools & Streaming text)
    const unsubChat = chatSocket.subscribe((data: any) => {
      if (data.type === 'THINKING') {
        useChatStore.getState().setThinking(true);
      } else if (data.type === 'TOOL_START' || data.type === 'TOOL_PROGRESS') {
        useChatStore.getState().setToolState({ toolName: data.tool, message: data.message, status: 'running' });
      } else if (data.type === 'STREAM_START') {
        currentStreamIdRef.current = data.message_id;
        useChatStore.getState().setThinking(false);
        addMessage({
          id: data.message_id,
          role: 'assistant',
          content: '',
          timestamp: Date.now()
        });
      } else if (data.type === 'TOKEN') {
        if (currentStreamIdRef.current === data.message_id) {
          useChatStore.getState().appendToken(data.content, data.message_id);
        }
      } else if (data.type === 'FINAL_RESPONSE') {
        useChatStore.getState().setThinking(false);
        useChatStore.getState().clearActiveTools();
        
        if (currentStreamIdRef.current === data.message_id) {
          // Replace content with verified full content to ensure clean markdown rendering
          useChatStore.setState((state) => ({
            messages: state.messages.map((m) =>
              m.id === data.message_id ? { ...m, content: data.content } : m
            )
          }));
          currentStreamIdRef.current = null;
        } else {
          // Fast-path tool responses
          addMessage({
            id: data.message_id || Date.now().toString(),
            role: 'assistant',
            content: data.content,
            timestamp: Date.now()
          });
        }
      }
    });

    // 3. Subscribe to Tier 3 Security Pauses
    const unsubConfirm = confirmSocket.subscribe((data: any) => {
      if (data.type === 'ACTION_PENDING') {
        // Attempt to spawn the OS-level window if we are backgrounded
        window.electronAPI.spawnConfirmationWindow(data.token, data.message).then((spawnedStandalone: boolean) => {
          if (!spawnedStandalone) {
            // We are focused, show the inline modal overlay
            useConfirmationStore.getState().addAction({
              token: data.token,
              tool_name: data.tool_name,
              tier: data.tier,
              message: data.message,
              expires_at: Date.now() + 60000
            });
          }
        });
      }
    });

    return () => {
      unsubChat();
      unsubConfirm();
    };
  }, []);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const msg: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: Date.now()
    };
    addMessage(msg);
    setInput('');
    useChatStore.getState().setThinking(true);

    try {
      if (chatSocket.isConnected()) {
        // Fast streaming channel over WebSocket
        chatSocket.send(msg.content);
      } else {
        // Standard REST fallback
        const data = await ChatAPI.sendMessage(msg.content);
        useChatStore.getState().setThinking(false);
        useChatStore.getState().clearActiveTools();
        addMessage({
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: data.response,
          timestamp: Date.now()
        });
      }
    } catch (err) {
      console.error('[EZIO] Chat error:', err);
      useChatStore.getState().setThinking(false);
      addMessage({
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your request. Please check that the backend is running.',
        timestamp: Date.now()
      });
    }
  };

  return (
    <div className="flex flex-col h-full relative bg-[url('https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=2564&auto=format&fit=crop')] bg-cover bg-center">
      <div className="absolute inset-0 bg-zinc-950/90 backdrop-blur-3xl z-0"></div>
      
      <div className="relative z-10 flex flex-col h-full">
        <ConfirmationModal />
        
        <ChatWindow />
        
        {/* Input Area */}
        <div className="absolute bottom-0 w-full bg-gradient-to-t from-zinc-950 via-zinc-950/90 to-transparent pb-8 pt-16 px-6">
          <form onSubmit={handleSend} className="max-w-4xl mx-auto relative group">
            <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl blur opacity-30 group-focus-within:opacity-100 transition duration-500"></div>
            <div className="relative flex items-center">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask EZIO to do anything..."
                className="w-full bg-zinc-900/90 backdrop-blur-xl border border-white/10 rounded-2xl py-4 pl-6 pr-14 text-white placeholder-zinc-400 focus:outline-none focus:ring-2 focus:ring-blue-500/50 shadow-2xl transition-all"
              />
              <button 
                type="submit"
                disabled={!input.trim()}
                className="absolute right-3 p-2 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:bg-zinc-800 disabled:text-zinc-600 text-white transition-all duration-200"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M12 5l7 7-7 7" />
                </svg>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Home;
