declare global {
  interface Window {
    electronAPI: {
      onConfirmationRequest: (callback: (data: any) => void) => void;
      resolveConfirmation: (token: string, approved: boolean) => void;
      spawnConfirmationWindow: (token: string, message: string) => Promise<boolean>;
      closeConfirmationWindow: () => void;
    }
  }
}

export {};
