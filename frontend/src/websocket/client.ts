type SocketMessageCallback = (data: any) => void;

class WebSocketClient {
  private socket: WebSocket | null = null;
  private url: string;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectTimeouts = [1000, 2000, 5000, 10000, 30000]; // Exponential backoff
  private onMessageCallbacks: SocketMessageCallback[] = [];

  constructor(endpoint: string) {
    this.url = `ws://localhost:8000/ws/${endpoint}`;
  }

  public connect() {
    if (this.socket && (this.socket.readyState === WebSocket.OPEN || this.socket.readyState === WebSocket.CONNECTING)) {
      return;
    }

    this.socket = new WebSocket(this.url);

    this.socket.onopen = () => {
      console.log(`Connected to ${this.url}`);
      this.reconnectAttempts = 0;
    };

    this.socket.onmessage = (event) => {
      let data = event.data;
      try {
        if (typeof data === 'string') data = JSON.parse(data);
      } catch (e) {
        // Leave as string/blob if not JSON
      }
      this.onMessageCallbacks.forEach(cb => cb(data));
    };

    this.socket.onclose = () => {
      console.log(`Disconnected from ${this.url}`);
      this.attemptReconnect();
    };
    
    this.socket.onerror = (err) => {
      console.error(`WebSocket error on ${this.url}`, err);
    };
  }

  private attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      const timeout = this.reconnectTimeouts[this.reconnectAttempts];
      console.log(`Reconnecting to ${this.url} in ${timeout}ms...`);
      setTimeout(() => this.connect(), timeout);
      this.reconnectAttempts++;
    } else {
      console.error(`Max reconnect attempts reached for ${this.url}`);
    }
  }

  public subscribe(callback: SocketMessageCallback) {
    this.onMessageCallbacks.push(callback);
    return () => {
      this.onMessageCallbacks = this.onMessageCallbacks.filter(cb => cb !== callback);
    };
  }

  public send(data: any) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      const payload = typeof data === 'string' ? data : JSON.stringify(data);
      this.socket.send(payload);
    } else {
      console.warn(`Cannot send, socket ${this.url} is not open`);
    }
  }

  public isConnected(): boolean {
    return this.socket !== null && this.socket.readyState === WebSocket.OPEN;
  }
}

// Export singleton instances for each separated socket
export const chatSocket = new WebSocketClient('chat');
export const confirmSocket = new WebSocketClient('confirmations');
export const voiceSocket = new WebSocketClient('voice');
