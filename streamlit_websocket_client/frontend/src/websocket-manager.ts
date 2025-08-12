/**
 * WebSocket Manager for handling connection lifecycle,
 * reconnection logic, and message queuing
 */

export interface WebSocketConfig {
  url: string;
  protocols?: string[];
  autoReconnect?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  onMessage?: (data: any) => void;
  onStateChange?: (state: WebSocketState) => void;
  onError?: (error: string) => void;
}

export interface WebSocketState {
  state: "CONNECTING" | "OPEN" | "CLOSED" | "ERROR";
  last_message: any;
  error: string | null;
  ready_state: number;
}

export class WebSocketManager {
  private config: Required<WebSocketConfig>;
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private reconnectTimeout: NodeJS.Timeout | null = null;
  private messageQueue: any[] = [];
  private isDestroyed = false;

  constructor(config: WebSocketConfig) {
    this.config = {
      protocols: [],
      autoReconnect: true,
      reconnectInterval: 3000,
      maxReconnectAttempts: 5,
      onMessage: () => {},
      onStateChange: () => {},
      onError: () => {},
      ...config,
    };
  }

  connect(): void {
    if (this.isDestroyed) return;

    try {
      // Clean up existing connection
      this.cleanup();

      // Create new WebSocket
      this.ws = new WebSocket(this.config.url, this.config.protocols);
      this.setupEventHandlers();
      
      // Update state
      this.updateState("CONNECTING");
    } catch (error) {
      this.handleError(error);
    }
  }

  private setupEventHandlers(): void {
    if (!this.ws) return;

    this.ws.onopen = () => {
      console.log("WebSocket connected to", this.config.url);
      this.reconnectAttempts = 0;
      this.updateState("OPEN");
      this.flushMessageQueue();
    };

    this.ws.onmessage = (event) => {
      console.log("WebSocket message received:", event.data);
      let messageData: any;

      try {
        // Try to parse as JSON
        messageData = JSON.parse(event.data);
      } catch {
        // If not JSON, use raw string
        messageData = event.data;
      }

      this.config.onMessage(messageData);
      this.updateState("OPEN", messageData);
    };

    this.ws.onerror = (error) => {
      console.error("WebSocket error:", error);
      this.updateState("ERROR", null, "WebSocket connection error");
      this.config.onError("WebSocket connection error");
    };

    this.ws.onclose = (event) => {
      console.log("WebSocket closed:", event.code, event.reason);
      
      const errorMessage = event.reason || 
        (event.code === 1006 ? "Connection lost" : `Closed with code ${event.code}`);
      
      this.updateState("CLOSED", null, errorMessage);
      
      // Handle reconnection
      if (this.shouldReconnect()) {
        this.scheduleReconnect();
      }
    };
  }

  private shouldReconnect(): boolean {
    return (
      !this.isDestroyed &&
      this.config.autoReconnect &&
      this.reconnectAttempts < this.config.maxReconnectAttempts
    );
  }

  private scheduleReconnect(): void {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
    }

    this.reconnectAttempts++;
    const delay = this.getReconnectDelay();
    
    console.log(
      `Scheduling reconnection attempt ${this.reconnectAttempts}/${this.config.maxReconnectAttempts} in ${delay}ms`
    );

    this.reconnectTimeout = setTimeout(() => {
      if (!this.isDestroyed) {
        this.connect();
      }
    }, delay);
  }

  private getReconnectDelay(): number {
    // Exponential backoff with jitter
    const baseDelay = this.config.reconnectInterval;
    const exponentialDelay = Math.min(
      baseDelay * Math.pow(1.5, this.reconnectAttempts - 1),
      30000 // Max 30 seconds
    );
    const jitter = Math.random() * 1000; // 0-1 second jitter
    return exponentialDelay + jitter;
  }

  send(message: any): boolean {
    if (!this.ws) {
      console.warn("WebSocket not initialized");
      return false;
    }

    if (this.ws.readyState === WebSocket.OPEN) {
      try {
        this.ws.send(message);
        return true;
      } catch (error) {
        console.error("Failed to send message:", error);
        this.handleError(error);
        return false;
      }
    } else {
      // Queue message for later
      console.log("WebSocket not ready, queueing message");
      this.messageQueue.push(message);
      return false;
    }
  }

  private flushMessageQueue(): void {
    while (this.messageQueue.length > 0 && this.ws?.readyState === WebSocket.OPEN) {
      const message = this.messageQueue.shift();
      this.send(message);
    }
  }

  private updateState(
    state: WebSocketState["state"],
    lastMessage?: any,
    error?: string | null
  ): void {
    const newState: WebSocketState = {
      state,
      last_message: lastMessage ?? null,
      error: error ?? null,
      ready_state: this.ws?.readyState ?? 3,
    };
    
    this.config.onStateChange(newState);
  }

  private handleError(error: any): void {
    const errorMessage = error instanceof Error ? error.message : String(error);
    console.error("WebSocket error:", errorMessage);
    this.updateState("ERROR", null, errorMessage);
    this.config.onError(errorMessage);
  }

  private cleanup(): void {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }

    if (this.ws) {
      // Remove handlers to prevent memory leaks
      this.ws.onopen = null;
      this.ws.onmessage = null;
      this.ws.onerror = null;
      this.ws.onclose = null;

      if (this.ws.readyState === WebSocket.OPEN || 
          this.ws.readyState === WebSocket.CONNECTING) {
        this.ws.close();
      }
      
      this.ws = null;
    }
  }

  destroy(): void {
    this.isDestroyed = true;
    this.cleanup();
    this.messageQueue = [];
  }

  getState(): WebSocketState {
    return {
      state: this.ws ? 
        (["CONNECTING", "OPEN", "CLOSING", "CLOSED"][this.ws.readyState] as any) || "CLOSED" 
        : "CLOSED",
      last_message: null,
      error: null,
      ready_state: this.ws?.readyState ?? 3,
    };
  }
}