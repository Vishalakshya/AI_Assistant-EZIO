import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: number;
}

export interface ToolState {
  toolName: string;
  message: string;
  status: 'running' | 'completed' | 'failed';
}

interface ChatStore {
  messages: ChatMessage[];
  activeTools: ToolState[];
  isThinking: boolean;
  addMessage: (message: ChatMessage) => void;
  appendToken: (token: string, messageId: string) => void;
  setThinking: (thinking: boolean) => void;
  setToolState: (state: ToolState) => void;
  clearActiveTools: () => void;
  clearHistory: () => void;
}

export const useChatStore = create<ChatStore>()(
  persist(
    (set) => ({
      messages: [],
      activeTools: [],
      isThinking: false,
      
      addMessage: (message) => 
        set((state) => ({ messages: [...state.messages, message] })),
        
      appendToken: (token, messageId) => 
        set((state) => ({
          messages: state.messages.map((m) => 
            m.id === messageId ? { ...m, content: m.content + token } : m
          )
        })),
        
      setThinking: (thinking) => set({ isThinking: thinking }),
      
      setToolState: (toolState) => 
        set((state) => {
          // Update existing tool or add new one
          const existing = state.activeTools.find(t => t.toolName === toolState.toolName);
          if (existing) {
            return {
              activeTools: state.activeTools.map(t => 
                t.toolName === toolState.toolName ? toolState : t
              )
            };
          }
          return { activeTools: [...state.activeTools, toolState] };
        }),
        
      clearActiveTools: () => set({ activeTools: [] }),
      
      clearHistory: () => set({ messages: [] })
    }),
    {
      name: 'ezio-chat-storage', // Persisted to localStorage
      partialize: (state) => ({ messages: state.messages }), // Only persist messages, not activeTools/isThinking
    }
  )
);
