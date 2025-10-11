'use client';

import { useEffect } from 'react';
import { initializeAuth } from '@/lib/shopify/customer-simple';

/**
 * ClientInitializer Component
 * Handles client-side initialization tasks like authentication
 * This component runs only on the client side and initializes auth on mount
 */
export default function ClientInitializer() {
  useEffect(() => {
    // Initialize authentication on app load
    initializeAuth().catch((error) => {
      console.error('Failed to initialize auth:', error);
    });
  }, []);

  // This component doesn't render anything
  return null;
}
