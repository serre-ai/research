'use client';

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from 'react';
import type { ReactNode } from 'react';

interface WebSocketMessage {
  channel: string;
  event: string;
  data: unknown;
}

type MessageHandler = (msg: WebSocketMessage) => void;

interface WebSocketContextType {
  connected: boolean;
  subscribe: (channel: string) => void;
  unsubscribe: (channel: string) => void;
  onMessage: (handler: MessageHandler) => () => void;
}

const WebSocketContext = createContext<WebSocketContextType>({
  connected: false,
  subscribe: () => {},
  unsubscribe: () => {},
  onMessage: () => () => {},
});

const RECONNECT_DELAYS = [1000, 2000, 5000, 10_000, 30_000];

export function WebSocketProvider({ children }: { children: ReactNode }) {
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const handlersRef = useRef<Set<MessageHandler>>(new Set());
  const reconnectAttemptRef = useRef(0);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout>>(undefined);
  const subscribedChannelsRef = useRef<Set<string>>(new Set());

  const connect = useCallback(async () => {
    try {
      // Get WebSocket URL with auth token from the Next.js API route
      const res = await fetch('/api/ws-token');
      if (!res.ok) return;
      const { url } = await res.json();

      // Connect directly to VPS WebSocket (Vercel can't hold long-lived WS)
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        setConnected(true);
        reconnectAttemptRef.current = 0;
        // Re-subscribe to all channels after reconnect
        for (const channel of subscribedChannelsRef.current) {
          ws.send(JSON.stringify({ type: 'subscribe', channel }));
        }
      };

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data as string) as WebSocketMessage;
          handlersRef.current.forEach((handler) => handler(msg));
        } catch {
          // Ignore non-JSON messages
        }
      };

      ws.onclose = () => {
        setConnected(false);
        wsRef.current = null;
        // Reconnect with exponential backoff
        const delay =
          RECONNECT_DELAYS[
            Math.min(
              reconnectAttemptRef.current,
              RECONNECT_DELAYS.length - 1,
            )
          ];
        reconnectAttemptRef.current++;
        reconnectTimerRef.current = setTimeout(connect, delay);
      };

      ws.onerror = () => {
        ws.close();
      };
    } catch {
      // Token fetch failed — retry with backoff
      const delay =
        RECONNECT_DELAYS[
          Math.min(reconnectAttemptRef.current, RECONNECT_DELAYS.length - 1)
        ];
      reconnectAttemptRef.current++;
      reconnectTimerRef.current = setTimeout(connect, delay);
    }
  }, []);

  useEffect(() => {
    connect();
    return () => {
      clearTimeout(reconnectTimerRef.current);
      wsRef.current?.close();
    };
  }, [connect]);

  const subscribe = useCallback((channel: string) => {
    subscribedChannelsRef.current.add(channel);
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'subscribe', channel }));
    }
  }, []);

  const unsubscribe = useCallback((channel: string) => {
    subscribedChannelsRef.current.delete(channel);
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'unsubscribe', channel }));
    }
  }, []);

  const onMessage = useCallback((handler: MessageHandler) => {
    handlersRef.current.add(handler);
    return () => {
      handlersRef.current.delete(handler);
    };
  }, []);

  return (
    <WebSocketContext.Provider
      value={{ connected, subscribe, unsubscribe, onMessage }}
    >
      {children}
    </WebSocketContext.Provider>
  );
}

export function useWebSocket() {
  return useContext(WebSocketContext);
}
