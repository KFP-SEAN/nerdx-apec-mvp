import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import {
  Cart,
  cartCreate,
  cartGet,
  cartLinesAdd,
  cartLinesUpdate,
  cartLinesRemove,
  getOrCreateCart
} from './shopify/cart';
import toast from 'react-hot-toast';

// Cart Store with Shopify Integration
interface CartStore {
  cart: Cart | null;
  isLoading: boolean;
  error: string | null;
  addItem: (variantId: string, quantity: number) => Promise<void>;
  updateItem: (lineId: string, quantity: number) => Promise<void>;
  removeItem: (lineId: string) => Promise<void>;
  clearCart: () => void;
  syncWithServer: () => Promise<void>;
  getTotalItems: () => number;
  getTotalPrice: () => number;
}

export const useCartStore = create<CartStore>()(
  persist(
    (set, get) => ({
      cart: null,
      isLoading: false,
      error: null,

      addItem: async (variantId: string, quantity: number) => {
        set({ isLoading: true, error: null });
        try {
          const currentCart = get().cart;

          if (!currentCart) {
            // Create new cart
            const newCart = await cartCreate([
              { merchandiseId: variantId, quantity }
            ]);
            set({ cart: newCart, isLoading: false });
          } else {
            // Add to existing cart
            const updatedCart = await cartLinesAdd(
              currentCart.id,
              [{ merchandiseId: variantId, quantity }]
            );
            set({ cart: updatedCart, isLoading: false });
          }

          toast.success('Added to cart');
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Failed to add to cart';
          set({ isLoading: false, error: errorMessage });
          toast.error(errorMessage);
          throw error;
        }
      },

      updateItem: async (lineId: string, quantity: number) => {
        set({ isLoading: true, error: null });
        try {
          const currentCart = get().cart;
          if (!currentCart) {
            set({ isLoading: false });
            return;
          }

          const updatedCart = await cartLinesUpdate(
            currentCart.id,
            [{ id: lineId, quantity }]
          );
          set({ cart: updatedCart, isLoading: false });
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Failed to update quantity';
          set({ isLoading: false, error: errorMessage });
          toast.error(errorMessage);
          throw error;
        }
      },

      removeItem: async (lineId: string) => {
        set({ isLoading: true, error: null });
        try {
          const currentCart = get().cart;
          if (!currentCart) {
            set({ isLoading: false });
            return;
          }

          const updatedCart = await cartLinesRemove(
            currentCart.id,
            [lineId]
          );
          set({ cart: updatedCart, isLoading: false });
          toast.success('Item removed from cart');
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Failed to remove item';
          set({ isLoading: false, error: errorMessage });
          toast.error(errorMessage);
          throw error;
        }
      },

      clearCart: () => {
        set({ cart: null });
        if (typeof window !== 'undefined') {
          localStorage.removeItem('cartId');
        }
        toast.success('Cart cleared');
      },

      syncWithServer: async () => {
        if (typeof window === 'undefined') return;

        const cartId = localStorage.getItem('cartId');
        if (!cartId) {
          set({ cart: null });
          return;
        }

        try {
          const cart = await cartGet(cartId);
          set({ cart });
        } catch (error) {
          // Cart not found or expired
          console.warn('Cart not found, clearing local storage');
          localStorage.removeItem('cartId');
          set({ cart: null });
        }
      },

      getTotalItems: () => {
        const cart = get().cart;
        return cart?.totalQuantity || 0;
      },

      getTotalPrice: () => {
        const cart = get().cart;
        return cart ? parseFloat(cart.cost.totalAmount.amount) : 0;
      },
    }),
    {
      name: 'cart-storage',
      partialize: (state) => ({ cart: state.cart }),
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
