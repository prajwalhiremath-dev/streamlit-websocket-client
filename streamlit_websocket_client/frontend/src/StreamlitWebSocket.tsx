import React, { useEffect, useRef, useState } from "react";
import {
  Streamlit,
  StreamlitComponentBase,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib";
import { WebSocketManager, WebSocketState } from "./websocket-manager";

interface StreamlitWebSocketProps extends ComponentProps {
  args: {
    url: string;
    headers?: Record<string, string>;
    protocols?: string[];
    auto_reconnect?: boolean;
    reconnect_interval?: number;
    max_reconnect_attempts?: number;
    send_message?: string;
  };
}

const StreamlitWebSocket: React.FC<StreamlitWebSocketProps> = ({ args }) => {
  const wsManagerRef = useRef<WebSocketManager | null>(null);
  const lastSentMessageRef = useRef<string | null>(null);
  const [isInitialized, setIsInitialized] = useState(false);

  // Initialize WebSocket manager
  useEffect(() => {
    // Create WebSocket manager
    const manager = new WebSocketManager({
      url: args.url,
      protocols: args.protocols,
      autoReconnect: args.auto_reconnect !== false,
      reconnectInterval: args.reconnect_interval || 3000,
      maxReconnectAttempts: args.max_reconnect_attempts || 5,
      onMessage: (data) => {
        // Update Streamlit with new message
        const state = manager.getState();
        Streamlit.setComponentValue({
          ...state,
          last_message: data,
        });
      },
      onStateChange: (state: WebSocketState) => {
        // Update Streamlit with state change
        Streamlit.setComponentValue(state);
      },
      onError: (error) => {
        console.error("WebSocket error in component:", error);
      },
    });

    wsManagerRef.current = manager;
    manager.connect();
    setIsInitialized(true);

    // Cleanup on unmount
    return () => {
      manager.destroy();
      wsManagerRef.current = null;
    };
  }, [args.url]); // Recreate if URL changes

  // Handle sending messages
  useEffect(() => {
    if (
      isInitialized &&
      args.send_message &&
      args.send_message !== lastSentMessageRef.current &&
      wsManagerRef.current
    ) {
      console.log("Sending message via manager:", args.send_message);
      const sent = wsManagerRef.current.send(args.send_message);
      if (sent) {
        lastSentMessageRef.current = args.send_message;
      }
    }
  }, [args.send_message, isInitialized]);

  // Notify Streamlit that we're ready
  useEffect(() => {
    Streamlit.setFrameHeight(0); // Invisible component
  }, []);

  // Invisible component (no UI)
  return null;
};

export default withStreamlitConnection(StreamlitWebSocket);