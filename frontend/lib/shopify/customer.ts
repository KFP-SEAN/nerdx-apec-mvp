/**
 * Shopify Customer Authentication Module
 * Handles customer signup, signin, and profile management
 */

import { shopifyStorefrontFetch, shopifyAdminFetch } from './client';
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

/**
 * Sign Up - Create new customer account
 */
export async function signUp(input: SignUpInput): Promise<Customer> {
  const mutation = `
    mutation customerCreate($input: CustomerCreateInput!) {
      customerCreate(input: $input) {
        customer {
          id
          email
          firstName
          lastName
          phone
          acceptsMarketing
        }
        customerUserErrors {
          field
          message
          code
        }
      }
    }
  `;

  try {
    const response = await shopifyStorefrontFetch<any>(mutation, {
      input: {
        email: input.email,
        password: input.password,
        firstName: input.firstName,
        lastName: input.lastName,
        phone: input.phone,
        acceptsMarketing: input.acceptsMarketing || false,
      },
    });

    if (
      response.customerCreate.customerUserErrors &&
      response.customerCreate.customerUserErrors.length > 0
    ) {
      const error = response.customerCreate.customerUserErrors[0];
      throw new ValidationError(error.message);
    }

    const customer = response.customerCreate.customer;

    // Auto sign in after signup
    if (customer) {
      try {
        await signIn({
          email: input.email,
          password: input.password,
          rememberMe: true,
        });
      } catch (error) {
        console.warn('Auto sign-in after signup failed:', error);
      }
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
  const mutation = `
    mutation customerAccessTokenCreate($input: CustomerAccessTokenCreateInput!) {
      customerAccessTokenCreate(input: $input) {
        customerAccessToken {
          accessToken
          expiresAt
        }
        customerUserErrors {
          field
          message
          code
        }
      }
    }
  `;

  try {
    const response = await shopifyStorefrontFetch<any>(mutation, {
      input: {
        email: input.email,
        password: input.password,
      },
    });

    if (
      response.customerAccessTokenCreate.customerUserErrors &&
      response.customerAccessTokenCreate.customerUserErrors.length > 0
    ) {
      throw new AuthenticationError('Invalid email or password');
    }

    const tokenData = response.customerAccessTokenCreate.customerAccessToken;

    if (!tokenData) {
      throw new AuthenticationError('Failed to create access token');
    }

    // Get customer details
    const customer = await getCustomer(tokenData.accessToken);

    // Store in Zustand
    useUserStore.getState().setUser({
      id: customer.id,
      email: customer.email,
      name: `${customer.firstName} ${customer.lastName}`,
      avatar: undefined,
    });

    // Store token in localStorage if remember me
    if (input.rememberMe) {
      if (typeof window !== 'undefined') {
        localStorage.setItem('customerAccessToken', tokenData.accessToken);
        localStorage.setItem('customerTokenExpiry', tokenData.expiresAt);
      }
    }

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
  const query = `
    query getCustomer($customerAccessToken: String!) {
      customer(customerAccessToken: $customerAccessToken) {
        id
        email
        firstName
        lastName
        phone
        acceptsMarketing
      }
    }
  `;

  try {
    const response = await shopifyStorefrontFetch<any>(query, {
      customerAccessToken: accessToken,
    });

    if (!response.customer) {
      throw new AuthenticationError('Customer not found');
    }

    return response.customer;
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
    const token = typeof window !== 'undefined' ? localStorage.getItem('customerAccessToken') : null;

    if (token) {
      const mutation = `
        mutation customerAccessTokenDelete($customerAccessToken: String!) {
          customerAccessTokenDelete(customerAccessToken: $customerAccessToken) {
            deletedAccessToken
            deletedCustomerAccessTokenId
            userErrors {
              field
              message
            }
          }
        }
      `;

      await shopifyStorefrontFetch<any>(mutation, { customerAccessToken: token });
    }

    if (typeof window !== 'undefined') {
      localStorage.removeItem('customerAccessToken');
      localStorage.removeItem('customerTokenExpiry');
    }

    useUserStore.getState().clearUser();
  } catch (error) {
    console.error('Sign out error:', error);
    if (typeof window !== 'undefined') {
      localStorage.removeItem('customerAccessToken');
      localStorage.removeItem('customerTokenExpiry');
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

  if (!token || !expiry) return false;

  const expiryDate = new Date(expiry);
  const now = new Date();

  if (now >= expiryDate) {
    localStorage.removeItem('customerAccessToken');
    localStorage.removeItem('customerTokenExpiry');
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
  const mutation = `
    mutation customerRecover($email: String!) {
      customerRecover(email: $email) {
        customerUserErrors {
          field
          message
          code
        }
      }
    }
  `;

  try {
    const response = await shopifyStorefrontFetch<any>(mutation, { email });

    if (
      response.customerRecover.customerUserErrors &&
      response.customerRecover.customerUserErrors.length > 0
    ) {
      const error = response.customerRecover.customerUserErrors[0];
      throw new ValidationError(error.message);
    }
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
