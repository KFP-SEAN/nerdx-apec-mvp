/**
 * Newsletter & Email Marketing Module
 * Handles newsletter subscriptions, welcome emails, and discount code generation
 * Based on SHOPIFY_PRD.md Section 4.1 and 4.2
 */

import { shopifyAdminFetch } from './client';

// ===========================
// Types & Interfaces
// ===========================

export interface NewsletterInput {
  email: string;
  firstName?: string;
  source?: 'footer' | 'popup' | 'checkout';
}

export interface NewsletterResponse {
  success: boolean;
  couponCode?: string;
  message: string;
}

export interface DiscountCodeParams {
  code: string;
  type: 'PERCENTAGE' | 'FIXED_AMOUNT';
  value: number;
  usageLimit: number;
  customerEmail: string;
  expiresAt: Date;
}

// Custom Errors
export class NewsletterError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'NewsletterError';
  }
}

// ===========================
// Main Newsletter Functions
// ===========================

/**
 * Subscribe user to newsletter
 * Creates or updates Shopify customer with acceptsMarketing: true
 */
export async function subscribeToNewsletter(
  input: NewsletterInput
): Promise<NewsletterResponse> {
  try {
    // 1. Create or update Shopify Customer with marketing consent
    const mutation = `
      mutation customerCreate($input: CustomerInput!) {
        customerCreate(input: $input) {
          customer {
            id
            email
            acceptsMarketing
            firstName
          }
          customerUserErrors {
            field
            message
            code
          }
        }
      }
    `;

    const response = await shopifyAdminFetch(mutation, {
      input: {
        email: input.email,
        firstName: input.firstName || '고객님',
        acceptsMarketing: true,
        acceptsMarketingUpdatedAt: new Date().toISOString(),
        tags: ['newsletter', `source:${input.source}`, 'community'],
      },
    });

    // Check for errors
    if (
      response.data?.customerCreate?.customerUserErrors &&
      response.data.customerCreate.customerUserErrors.length > 0
    ) {
      const error = response.data.customerCreate.customerUserErrors[0];

      // If customer already exists, update their marketing consent
      if (error.code === 'TAKEN' || error.message?.includes('taken')) {
        await updateMarketingConsent(input.email, true);
        return {
          success: true,
          message: '구독 설정이 업데이트되었습니다',
        };
      }

      throw new NewsletterError(
        error.message || '구독에 실패했습니다'
      );
    }

    // 2. Generate welcome discount code
    const couponCode = `WELCOME15-${generateUniqueCode()}`;
    await createDiscountCode({
      code: couponCode,
      type: 'PERCENTAGE',
      value: 15,
      usageLimit: 1,
      customerEmail: input.email,
      expiresAt: addDays(new Date(), 30), // 30 days validity
    });

    // 3. Trigger welcome email (handled by Shopify or email service)
    await triggerWelcomeEmail({
      email: input.email,
      firstName: input.firstName || '고객님',
      couponCode,
    });

    // 4. Track analytics event
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('event', 'newsletter_subscribed', {
        source: input.source,
        email: input.email,
      });
    }

    return {
      success: true,
      couponCode,
      message: '구독이 완료되었습니다!',
    };
  } catch (error) {
    console.error('Newsletter subscription error:', error);
    throw error instanceof NewsletterError
      ? error
      : new NewsletterError('구독 처리 중 오류가 발생했습니다');
  }
}

/**
 * Update marketing consent for existing customer
 */
export async function updateMarketingConsent(
  email: string,
  acceptsMarketing: boolean
): Promise<void> {
  try {
    // First, get customer ID by email
    const queryCustomer = `
      query getCustomerByEmail($query: String!) {
        customers(first: 1, query: $query) {
          edges {
            node {
              id
              email
            }
          }
        }
      }
    `;

    const customerResponse = await shopifyAdminFetch(queryCustomer, {
      query: `email:${email}`,
    });

    const customers =
      customerResponse.data?.customers?.edges || [];
    if (customers.length === 0) {
      throw new NewsletterError('고객을 찾을 수 없습니다');
    }

    const customerId = customers[0].node.id;

    // Update customer marketing consent
    const mutation = `
      mutation customerUpdate($input: CustomerInput!) {
        customerUpdate(input: $input) {
          customer {
            id
            email
            acceptsMarketing
          }
          userErrors {
            field
            message
          }
        }
      }
    `;

    const response = await shopifyAdminFetch(mutation, {
      input: {
        id: customerId,
        acceptsMarketing,
        acceptsMarketingUpdatedAt: new Date().toISOString(),
      },
    });

    if (
      response.data?.customerUpdate?.userErrors &&
      response.data.customerUpdate.userErrors.length > 0
    ) {
      const error = response.data.customerUpdate.userErrors[0];
      throw new NewsletterError(
        error.message || '마케팅 동의 업데이트 실패'
      );
    }
  } catch (error) {
    console.error('Update marketing consent error:', error);
    throw error;
  }
}

/**
 * Create Shopify discount code
 */
export async function createDiscountCode(
  params: DiscountCodeParams
): Promise<void> {
  try {
    const mutation = `
      mutation priceRuleCreate($priceRule: PriceRuleInput!, $priceRuleDiscountCode: PriceRuleDiscountCodeInput!) {
        priceRuleCreate(priceRule: $priceRule, priceRuleDiscountCode: $priceRuleDiscountCode) {
          priceRule {
            id
            title
          }
          priceRuleDiscountCode {
            id
            code
          }
          priceRuleUserErrors {
            field
            message
          }
        }
      }
    `;

    const priceRuleInput = {
      title: `Newsletter Welcome - ${params.customerEmail}`,
      value:
        params.type === 'PERCENTAGE'
          ? `-${params.value}`
          : `-${params.value}`,
      valueType: params.type,
      customerSelection: {
        forAllCustomers: false,
      },
      target: {
        targetType: 'LINE_ITEM',
        targetAllLineItems: true,
      },
      allocationMethod: 'ACROSS',
      usageLimit: params.usageLimit,
      startsAt: new Date().toISOString(),
      endsAt: params.expiresAt.toISOString(),
    };

    const response = await shopifyAdminFetch(mutation, {
      priceRule: priceRuleInput,
      priceRuleDiscountCode: {
        code: params.code,
      },
    });

    if (
      response.data?.priceRuleCreate?.priceRuleUserErrors &&
      response.data.priceRuleCreate.priceRuleUserErrors.length > 0
    ) {
      const error =
        response.data.priceRuleCreate.priceRuleUserErrors[0];
      throw new NewsletterError(
        error.message || '할인 코드 생성 실패'
      );
    }

    console.log(
      `Discount code created: ${params.code} (${params.value}% off)`
    );
  } catch (error) {
    console.error('Create discount code error:', error);
    throw error;
  }
}

/**
 * Trigger welcome email
 * In production, this would integrate with Shopify Email or Klaviyo
 * For MVP, we'll log and rely on Shopify's automatic welcome email
 */
export async function triggerWelcomeEmail(params: {
  email: string;
  firstName: string;
  couponCode: string;
}): Promise<void> {
  try {
    console.log('Welcome email triggered:', {
      to: params.email,
      firstName: params.firstName,
      couponCode: params.couponCode,
      subject: '🍶 NERDX 커뮤니티에 오신 걸 환영합니다!',
    });

    // In production, integrate with email service
    // Option 1: Shopify Email API
    // Option 2: Klaviyo API
    // Option 3: Custom email service (SendGrid, AWS SES, etc.)

    // For now, Shopify will send automatic welcome email
    // when customer is created with acceptsMarketing: true

    // TODO: Implement actual email sending in production
    // await sendEmail({
    //   to: params.email,
    //   template: 'welcome-newsletter',
    //   data: {
    //     firstName: params.firstName,
    //     couponCode: params.couponCode,
    //     couponExpiry: '30일',
    //   },
    // });
  } catch (error) {
    console.error('Trigger welcome email error:', error);
    // Don't throw - email failure shouldn't block subscription
  }
}

// ===========================
// Helper Functions
// ===========================

/**
 * Generate unique 8-character code for discount codes
 */
export function generateUniqueCode(): string {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  let code = '';
  for (let i = 0; i < 8; i++) {
    code += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return code;
}

/**
 * Add days to date
 */
export function addDays(date: Date, days: number): Date {
  const result = new Date(date);
  result.setDate(result.getDate() + days);
  return result;
}

/**
 * Add hours to date
 */
export function addHours(date: Date, hours: number): Date {
  const result = new Date(date);
  result.setHours(result.getHours() + hours);
  return result;
}

/**
 * Validate email format
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * Get subscriber count from cookie/localStorage
 * This is a placeholder for social proof display
 */
export function getSubscriberCount(): number {
  if (typeof window === 'undefined') return 12453;

  const cached = localStorage.getItem('newsletter_subscriber_count');
  if (cached) {
    const { count, timestamp } = JSON.parse(cached);
    // Cache for 1 hour
    if (Date.now() - timestamp < 3600000) {
      return count;
    }
  }

  // Default fallback
  return 12453;
}

/**
 * Check if user has already subscribed
 * Check cookie to prevent duplicate subscriptions in same session
 */
export function hasRecentlySubscribed(): boolean {
  if (typeof window === 'undefined') return false;

  const subscribed = localStorage.getItem(
    'newsletter_subscribed_timestamp'
  );
  if (subscribed) {
    const timestamp = parseInt(subscribed, 10);
    // Consider "recently" as within last 7 days
    return Date.now() - timestamp < 7 * 24 * 60 * 60 * 1000;
  }

  return false;
}

/**
 * Mark user as subscribed
 */
export function markAsSubscribed(): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem(
    'newsletter_subscribed_timestamp',
    Date.now().toString()
  );
}

/**
 * Should show newsletter popup
 * Based on cookie and user behavior
 */
export function shouldShowNewsletterPopup(): boolean {
  if (typeof window === 'undefined') return false;

  // Don't show if user already subscribed
  if (hasRecentlySubscribed()) return false;

  // Check popup dismiss cookie
  const dismissed = localStorage.getItem('newsletter_popup_dismissed');
  if (dismissed) {
    const timestamp = parseInt(dismissed, 10);
    // Don't show again for 30 days
    return Date.now() - timestamp >= 30 * 24 * 60 * 60 * 1000;
  }

  return true;
}

/**
 * Dismiss newsletter popup
 */
export function dismissNewsletterPopup(): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem(
    'newsletter_popup_dismissed',
    Date.now().toString()
  );
}
