import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  isLoading?: boolean;
  media?: {
    type: 'image' | 'video';
    url: string;
    name: string;
  };
}

interface ChatState {
  sessionId: string;
  messages: Message[];
  isLoading: boolean;
  setSessionId: (id: string) => void;
  setMessages: (messages: Message[]) => void;
  addMessage: (message: Message) => void;
  updateMessage: (id: string, updates: Partial<Message>) => void;
  removeMessage: (id: string) => void;
  setIsLoading: (loading: boolean) => void;
  clearChat: () => void;
}

export const useChatStore = create<ChatState>()(
  persist(
    (set) => ({
      sessionId: `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      messages: [],
      isLoading: false,

      setSessionId: (id) => set({ sessionId: id }),

      setMessages: (messages) => set({ messages }),

      addMessage: (message) =>
        set((state) => ({
          messages: [...state.messages, message],
        })),

      updateMessage: (id, updates) =>
        set((state) => ({
          messages: state.messages.map((msg) =>
            msg.id === id ? { ...msg, ...updates } : msg
          ),
        })),

      removeMessage: (id) =>
        set((state) => ({
          messages: state.messages.filter((msg) => msg.id !== id),
        })),

      setIsLoading: (loading) => set({ isLoading: loading }),

      clearChat: () =>
        set({
          sessionId: `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          messages: [],
          isLoading: false,
        }),
    }),
    {
      name: 'chat-storage', // Key in sessionStorage
      storage: {
        getItem: (name) => {
          const str = sessionStorage.getItem(name);
          if (!str) return null;
          const { state } = JSON.parse(str);
          return {
            state: {
              ...state,
              // Convert timestamp strings back to Date objects
              messages: state.messages.map((msg: any) => ({
                ...msg,
                timestamp: new Date(msg.timestamp),
              })),
            },
          };
        },
        setItem: (name, value) => {
          sessionStorage.setItem(name, JSON.stringify(value));
        },
        removeItem: (name) => {
          sessionStorage.removeItem(name);
        },
      },
    }
  )
);
