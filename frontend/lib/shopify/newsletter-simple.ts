/**
 * Simplified Newsletter Module (Without Admin API)
 * For MVP - collects emails without Shopify Admin API dependency
 */

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

// Custom Errors
export class NewsletterError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'NewsletterError';
  }
}

/**
 * Subscribe user to newsletter
 * Saves to Shopify and stores locally
 */
export async function subscribeToNewsletter(
  input: NewsletterInput
): Promise<NewsletterResponse> {
  try {
    // Validate email
    if (!isValidEmail(input.email)) {
      throw new NewsletterError('올바른 이메일 주소를 입력해주세요');
    }

    // Check if already subscribed (simple check using localStorage)
    if (typeof window !== 'undefined') {
      const subscribed = localStorage.getItem(`newsletter_${input.email}`);
      if (subscribed) {
        return {
          success: true,
          message: '이미 구독하신 이메일입니다',
        };
      }
    }

    // Subscribe in Shopify via API
    let couponCode = 'WELCOME15';
    try {
      const response = await fetch('/api/customer/subscribe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: input.email.toLowerCase().trim(),
          firstName: input.firstName,
          source: input.source || 'footer',
        }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        console.log('Newsletter subscription saved to Shopify:', data.customer);
        if (data.couponCode) {
          couponCode = data.couponCode;
        }
      } else {
        console.warn('Failed to save to Shopify:', data.message);
        // Continue with local storage only
      }
    } catch (error: any) {
      console.warn('Shopify API error, continuing with local storage:', error);
      // Continue with local storage only
    }

    // Mark as subscribed in localStorage
    if (typeof window !== 'undefined') {
      localStorage.setItem(`newsletter_${input.email}`, Date.now().toString());
      localStorage.setItem('newsletter_subscribed_timestamp', Date.now().toString());
    }

    // Track analytics event
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('event', 'newsletter_subscribed', {
        source: input.source,
        email: input.email,
      });
    }

    return {
      success: true,
      couponCode,
      message: '구독이 완료되었습니다! 🎉',
    };
  } catch (error) {
    console.error('Newsletter subscription error:', error);
    throw error instanceof NewsletterError
      ? error
      : new NewsletterError('구독 처리 중 오류가 발생했습니다');
  }
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
