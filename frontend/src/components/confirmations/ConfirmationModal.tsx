import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useConfirmationStore } from '../../stores/useConfirmationStore';
import { confirmSocket } from '../../websocket/client';

const ConfirmationModal: React.FC = () => {
  const pendingActions = useConfirmationStore(state => state.pendingActions);
  
  if (pendingActions.length === 0) return null;
  
  const action = pendingActions[0]; // Show the first pending action

  const handleResolve = (approved: boolean) => {
    // Fire back to WebSocket
    confirmSocket.send({ token: action.token, approved });
    // Remove locally
    useConfirmationStore.getState().removeAction(action.token);
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
      >
        <motion.div
          initial={{ scale: 0.95, opacity: 0, y: 10 }}
          animate={{ scale: 1, opacity: 1, y: 0 }}
          className="bg-zinc-900 border border-zinc-800 rounded-xl shadow-2xl p-6 w-full max-w-md"
        >
          <div className="flex items-center space-x-3 text-red-400 mb-4">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <h2 className="text-lg font-semibold text-white">Action Required</h2>
          </div>
          
          <p className="text-zinc-300 text-sm mb-6 leading-relaxed">
            EZIO is requesting permission to execute a Tier {action.tier} command:<br/>
            <strong className="text-white mt-2 block">{action.message}</strong>
          </p>
          
          <div className="flex space-x-3 justify-end">
            <button 
              onClick={() => handleResolve(false)}
              className="px-4 py-2 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-300 transition-colors text-sm font-medium"
            >
              Deny
            </button>
            <button 
              onClick={() => handleResolve(true)}
              className="px-4 py-2 rounded-lg bg-red-600 hover:bg-red-500 text-white transition-colors text-sm font-medium"
            >
              Approve Action
            </button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default ConfirmationModal;
