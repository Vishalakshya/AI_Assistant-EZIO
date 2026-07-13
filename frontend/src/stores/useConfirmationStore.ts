import { create } from 'zustand';

export interface PendingAction {
  token: string;
  tool_name: string;
  tier: number;
  message: string;
  expires_at: number;
}

interface ConfirmationStore {
  pendingActions: PendingAction[];
  addAction: (action: PendingAction) => void;
  removeAction: (token: string) => void;
  clearAll: () => void;
}

// Confirmation store is deliberately NOT persisted. 
// Pending security prompts should vanish if the app restarts.
export const useConfirmationStore = create<ConfirmationStore>((set) => ({
  pendingActions: [],
  
  addAction: (action) => 
    set((state) => ({ pendingActions: [...state.pendingActions, action] })),
    
  removeAction: (token) => 
    set((state) => ({
      pendingActions: state.pendingActions.filter(a => a.token !== token)
    })),
    
  clearAll: () => set({ pendingActions: [] })
}));
