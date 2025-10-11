import { NextRequest, NextResponse } from 'next/server';
import { findCustomerByEmail } from '@/lib/shopify/admin';

/**
 * GET /api/newsletter/verify?email=test@example.com
 * Verify newsletter subscriber in Shopify
 */
export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const email = searchParams.get('email');

    if (!email) {
      return NextResponse.json(
        { success: false, message: 'Email parameter required' },
        { status: 400 }
      );
    }

    const customer = await findCustomerByEmail(email);

    if (!customer) {
      return NextResponse.json(
        {
          success: false,
          message: 'Customer not found in Shopify',
          email: email,
        },
        { status: 404 }
      );
    }

    // Check newsletter subscriber status
    const tags = customer.tags || [];
    const isNewsletterSubscriber = tags.includes('newsletter-subscriber');
    const isWebSignup = tags.includes('web-signup');
    const marketingStatus = customer.emailMarketingConsent?.marketingState;

    return NextResponse.json({
      success: true,
      found: true,
      customer: {
        id: customer.id,
        email: customer.email,
        firstName: customer.firstName,
        lastName: customer.lastName,
        tags: tags,
        isNewsletterSubscriber,
        isWebSignup,
        emailMarketingStatus: marketingStatus,
        marketingConsentUpdated: customer.emailMarketingConsent?.consentUpdatedAt,
      },
      storage: {
        location: 'Shopify Admin > Customers',
        adminUrl: `https://${process.env.SHOPIFY_DOMAIN || process.env.NEXT_PUBLIC_SHOPIFY_DOMAIN}/admin/customers`,
      },
    });
  } catch (error: any) {
    console.error('Verification error:', error);
    return NextResponse.json(
      { success: false, message: error.message },
      { status: 500 }
    );
  }
}
