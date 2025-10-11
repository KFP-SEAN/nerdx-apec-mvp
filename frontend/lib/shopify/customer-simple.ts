/**
 * Simplified Customer Authentication Module (Without Shopify API)
 * For MVP - uses localStorage for authentication
 */

import { useUserStore } from '../store';

// Types
export interface SignUpInput {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  phone?: string;
  acceptsMarketing?: boolean;
}

export interface SignInInput {
  email: string;
  password: string;
  rememberMe?: boolean;
}

export interface Customer {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  phone?: string;
  acceptsMarketing: boolean;
}

export interface AccessToken {
  accessToken: string;
  expiresAt: string;
}

export class AuthenticationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'AuthenticationError';
  }
}

export class ValidationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ValidationError';
  }
}

// Helper functions for localStorage
function getStoredCustomers(): Record<string, any> {
  if (typeof window === 'undefined') return {};
  try {
    const stored = localStorage.getItem('mvp_customers');
    return stored ? JSON.parse(stored) : {};
  } catch {
    return {};
  }
}

function setStoredCustomers(customers: Record<string, any>): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem('mvp_customers', JSON.stringify(customers));
}

function hashPassword(password: string): string {
  // Simple hash for MVP (NOT secure for production!)
  // In production, use bcrypt or similar server-side
  let hash = 0;
  for (let i = 0; i < password.length; i++) {
    const char = password.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }
  return hash.toString(36);
}

function generateCustomerId(): string {
  return 'cust_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

function generateAccessToken(): string {
  return 'token_' + Date.now() + '_' + Math.random().toString(36).substr(2, 16);
}

/**
 * Sign Up - Create new customer account
 */
export async function signUp(input: SignUpInput): Promise<Customer> {
  try {
    // Validate input
    if (!input.email || !input.password) {
      throw new ValidationError('Email and password are required');
    }

    if (input.password.length < 6) {
      throw new ValidationError('Password must be at least 6 characters');
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(input.email)) {
      throw new ValidationError('Please enter a valid email address');
    }

    // Check if email already exists in localStorage
    const customers = getStoredCustomers();
    const emailLower = input.email.toLowerCase();

    if (customers[emailLower]) {
      throw new ValidationError('An account with this email already exists');
    }

    // Create customer in Shopify via API
    let shopifyCustomerId = generateCustomerId();
    try {
      const response = await fetch('/api/customer/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: emailLower,
          firstName: input.firstName,
          lastName: input.lastName,
          phone: input.phone,
          acceptsMarketing: input.acceptsMarketing || false,
        }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        shopifyCustomerId = data.customer.id;
        console.log('Customer created in Shopify:', shopifyCustomerId);
      } else {
        if (data.alreadyExists) {
          throw new ValidationError('An account with this email already exists');
        }
        console.warn('Failed to create customer in Shopify:', data.message);
        // Continue with localStorage-only registration
      }
    } catch (error: any) {
      console.warn('Shopify API error, continuing with local storage:', error);
      // Continue with localStorage-only registration
    }

    // Create customer locally
    const customer: Customer = {
      id: shopifyCustomerId,
      email: emailLower,
      firstName: input.firstName,
      lastName: input.lastName,
      phone: input.phone,
      acceptsMarketing: input.acceptsMarketing || false,
    };

    // Store customer in localStorage
    customers[emailLower] = {
      ...customer,
      passwordHash: hashPassword(input.password),
      createdAt: new Date().toISOString(),
    };
    setStoredCustomers(customers);

    console.log('Customer created locally:', {
      id: customer.id,
      email: emailLower,
    });

    // Auto sign in after signup
    try {
      await signIn({
        email: input.email,
        password: input.password,
        rememberMe: true,
      });
    } catch (error) {
      console.warn('Auto sign-in after signup failed:', error);
    }

    return customer;
  } catch (error) {
    console.error('Sign up error:', error);
    throw error;
  }
}

/**
 * Sign In - Authenticate customer and get access token
 */
export async function signIn(input: SignInInput): Promise<AccessToken> {
  try {
    if (!input.email || !input.password) {
      throw new AuthenticationError('Email and password are required');
    }

    const customers = getStoredCustomers();
    const emailLower = input.email.toLowerCase();
    const storedCustomer = customers[emailLower];

    if (!storedCustomer) {
      throw new AuthenticationError('Invalid email or password');
    }

    // Verify password
    const passwordHash = hashPassword(input.password);
    if (storedCustomer.passwordHash !== passwordHash) {
      throw new AuthenticationError('Invalid email or password');
    }

    // Generate access token
    const accessToken = generateAccessToken();
    const expiresAt = new Date();
    expiresAt.setDate(expiresAt.getDate() + (input.rememberMe ? 30 : 1)); // 30 days or 1 day

    const tokenData: AccessToken = {
      accessToken,
      expiresAt: expiresAt.toISOString(),
    };

    // Store in Zustand
    useUserStore.getState().setUser({
      id: storedCustomer.id,
      email: storedCustomer.email,
      name: `${storedCustomer.firstName} ${storedCustomer.lastName}`,
      avatar: undefined,
    });

    // Store token in localStorage
    if (typeof window !== 'undefined') {
      localStorage.setItem('customerAccessToken', accessToken);
      localStorage.setItem('customerTokenExpiry', tokenData.expiresAt);
      localStorage.setItem('currentCustomerEmail', emailLower);
    }

    console.log('Customer signed in:', { email: emailLower });

    return tokenData;
  } catch (error) {
    console.error('Sign in error:', error);
    throw error;
  }
}

/**
 * Get Customer Details by Access Token
 */
export async function getCustomer(accessToken: string): Promise<Customer> {
  try {
    if (typeof window === 'undefined') {
      throw new AuthenticationError('Not in browser context');
    }

    const email = localStorage.getItem('currentCustomerEmail');
    if (!email) {
      throw new AuthenticationError('Customer not found');
    }

    const customers = getStoredCustomers();
    const storedCustomer = customers[email];

    if (!storedCustomer) {
      throw new AuthenticationError('Customer not found');
    }

    return {
      id: storedCustomer.id,
      email: storedCustomer.email,
      firstName: storedCustomer.firstName,
      lastName: storedCustomer.lastName,
      phone: storedCustomer.phone,
      acceptsMarketing: storedCustomer.acceptsMarketing,
    };
  } catch (error) {
    console.error('Get customer error:', error);
    throw error;
  }
}

/**
 * Sign Out - Clear user session
 */
export async function signOut(): Promise<void> {
  try {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('customerAccessToken');
      localStorage.removeItem('customerTokenExpiry');
      localStorage.removeItem('currentCustomerEmail');
    }

    useUserStore.getState().clearUser();
    console.log('Customer signed out');
  } catch (error) {
    console.error('Sign out error:', error);
    if (typeof window !== 'undefined') {
      localStorage.removeItem('customerAccessToken');
      localStorage.removeItem('customerTokenExpiry');
      localStorage.removeItem('currentCustomerEmail');
    }
    useUserStore.getState().clearUser();
  }
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  if (typeof window === 'undefined') return false;

  const token = localStorage.getItem('customerAccessToken');
  const expiry = localStorage.getItem('customerTokenExpiry');
  const email = localStorage.getItem('currentCustomerEmail');

  if (!token || !expiry || !email) return false;

  const expiryDate = new Date(expiry);
  const now = new Date();

  if (now >= expiryDate) {
    localStorage.removeItem('customerAccessToken');
    localStorage.removeItem('customerTokenExpiry');
    localStorage.removeItem('currentCustomerEmail');
    useUserStore.getState().clearUser();
    return false;
  }

  return true;
}

/**
 * Get current access token
 */
export function getAccessToken(): string | null {
  if (typeof window === 'undefined') return null;
  if (!isAuthenticated()) return null;
  return localStorage.getItem('customerAccessToken');
}

/**
 * Password Reset Request
 */
export async function requestPasswordReset(email: string): Promise<void> {
  try {
    const customers = getStoredCustomers();
    const emailLower = email.toLowerCase();

    if (!customers[emailLower]) {
      // Don't reveal if email exists for security
      console.log('Password reset requested for:', emailLower);
      return;
    }

    // In production, this would send an email
    console.log('Password reset email would be sent to:', emailLower);

    // For MVP, we'll just log it
    alert(`Password reset instructions would be sent to ${email}. For MVP, please contact support.`);
  } catch (error) {
    console.error('Password reset request error:', error);
    throw error;
  }
}

/**
 * Initialize authentication on app load
 */
export async function initializeAuth(): Promise<void> {
  if (!isAuthenticated()) return;

  try {
    const token = getAccessToken();
    if (token) {
      const customer = await getCustomer(token);
      useUserStore.getState().setUser({
        id: customer.id,
        email: customer.email,
        name: `${customer.firstName} ${customer.lastName}`,
        avatar: undefined,
      });
    }
  } catch (error) {
    console.error('Initialize auth error:', error);
    signOut();
  }
}

/**
 * Get all customers (for debugging only)
 */
export function getAllCustomers(): Customer[] {
  const customers = getStoredCustomers();
  return Object.values(customers).map((c: any) => ({
    id: c.id,
    email: c.email,
    firstName: c.firstName,
    lastName: c.lastName,
    phone: c.phone,
    acceptsMarketing: c.acceptsMarketing,
  }));
}
