import { create } from 'zustand';
import { persist } from 'zustand/middleware';

// Cart Store
interface CartItem {
  id: string;
  product_id: string;
  name: string;
  price: number;
  quantity: number;
  image_url: string;
}

interface CartStore {
  items: CartItem[];
  addItem: (item: CartItem) => void;
  removeItem: (id: string) => void;
  updateQuantity: (id: string, quantity: number) => void;
  clearCart: () => void;
  getTotalItems: () => number;
  getTotalPrice: () => number;
}

export const useCartStore = create<CartStore>()(
  persist(
    (set, get) => ({
      items: [],
      addItem: (item) => {
        const items = get().items;
        const existingItem = items.find((i) => i.product_id === item.product_id);

        if (existingItem) {
          set({
            items: items.map((i) =>
              i.product_id === item.product_id
                ? { ...i, quantity: i.quantity + item.quantity }
                : i
            ),
          });
        } else {
          set({ items: [...items, item] });
        }
      },
      removeItem: (id) => {
        set({ items: get().items.filter((i) => i.id !== id) });
      },
      updateQuantity: (id, quantity) => {
        if (quantity <= 0) {
          get().removeItem(id);
        } else {
          set({
            items: get().items.map((i) =>
              i.id === id ? { ...i, quantity } : i
            ),
          });
        }
      },
      clearCart: () => set({ items: [] }),
      getTotalItems: () => {
        return get().items.reduce((sum, item) => sum + item.quantity, 0);
      },
      getTotalPrice: () => {
        return get().items.reduce(
          (sum, item) => sum + item.price * item.quantity,
          0
        );
      },
    }),
    {
      name: 'cart-storage',
    }
  )
);

// User Store
interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
}

interface UserStore {
  user: User | null;
  isAuthenticated: boolean;
  setUser: (user: User) => void;
  clearUser: () => void;
}

export const useUserStore = create<UserStore>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      setUser: (user) => set({ user, isAuthenticated: true }),
      clearUser: () => set({ user: null, isAuthenticated: false }),
    }),
    {
      name: 'user-storage',
    }
  )
);

// Chat Store
interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface ChatStore {
  messages: ChatMessage[];
  sessionId: string | null;
  addMessage: (message: ChatMessage) => void;
  clearMessages: () => void;
  setSessionId: (id: string) => void;
}

export const useChatStore = create<ChatStore>()(
  persist(
    (set) => ({
      messages: [],
      sessionId: null,
      addMessage: (message) => {
        set((state) => ({ messages: [...state.messages, message] }));
      },
      clearMessages: () => set({ messages: [] }),
      setSessionId: (id) => set({ sessionId: id }),
    }),
    {
      name: 'chat-storage',
    }
  )
);

// Wishlist Store
interface WishlistItem {
  id: string;
  product_id: string;
  name: string;
  price: number;
  image_url: string;
  added_at: Date;
}

interface WishlistStore {
  items: WishlistItem[];
  addItem: (item: Omit<WishlistItem, 'added_at'>) => void;
  removeItem: (product_id: string) => void;
  isInWishlist: (product_id: string) => boolean;
  clearWishlist: () => void;
}

export const useWishlistStore = create<WishlistStore>()(
  persist(
    (set, get) => ({
      items: [],
      addItem: (item) => {
        const items = get().items;
        if (!items.find((i) => i.product_id === item.product_id)) {
          set({
            items: [...items, { ...item, added_at: new Date() }],
          });
        }
      },
      removeItem: (product_id) => {
        set({
          items: get().items.filter((i) => i.product_id !== product_id),
        });
      },
      isInWishlist: (product_id) => {
        return get().items.some((i) => i.product_id === product_id);
      },
      clearWishlist: () => set({ items: [] }),
    }),
    {
      name: 'wishlist-storage',
    }
  )
);
