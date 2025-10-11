import { NextRequest, NextResponse } from 'next/server';
import {
  createShopifyCustomer,
  findCustomerByEmail,
  updateCustomerMarketing,
  addCustomerTags,
  createDiscountCode
} from '@/lib/shopify/admin';

/**
 * POST /api/newsletter/subscribe
 * Subscribe user to newsletter and generate welcome discount code
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { email, source, firstName } = body;

    // Validate input
    if (!email || typeof email !== 'string') {
      return NextResponse.json(
        { success: false, message: '이메일 주소가 필요합니다' },
        { status: 400 }
      );
    }

    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return NextResponse.json(
        { success: false, message: '올바른 이메일 주소를 입력해주세요' },
        { status: 400 }
      );
    }

    // Validate source
    const validSources = ['footer', 'popup', 'checkout'];
    if (source && !validSources.includes(source)) {
      return NextResponse.json(
        {
          success: false,
          message: 'Invalid source parameter'
        },
        { status: 400 }
      );
    }

    const emailLower = email.toLowerCase().trim();

    // Check if customer already exists
    let customer = await findCustomerByEmail(emailLower);

    if (customer) {
      // Update existing customer
      await updateCustomerMarketing(customer.id, true);

      // Add newsletter tag if not present
      const tags = customer.tags || [];
      if (!tags.includes('newsletter-subscriber')) {
        await addCustomerTags(customer.id, ['newsletter-subscriber']);
      }

      console.log('Updated existing customer:', customer.id);
    } else {
      // Create new customer
      customer = await createShopifyCustomer({
        email: emailLower,
        firstName: firstName || 'Guest',
        lastName: 'Customer',
        acceptsMarketing: true,
        tags: ['newsletter-subscriber', 'web-signup'],
      });

      console.log('Created new customer:', customer.id);
    }

    // Ensure WELCOME15 discount code exists
    try {
      await createDiscountCode({
        code: 'WELCOME15',
        percentage: 15,
        usageLimit: undefined, // Unlimited
      });
    } catch (error) {
      // Code might already exist, that's okay
      console.log('Discount code already exists or error creating:', error);
    }

    // Return success response
    return NextResponse.json({
      success: true,
      message: '구독이 완료되었습니다! 🎉',
      couponCode: 'WELCOME15',
      customer: {
        id: customer.id,
        email: customer.email,
      },
    }, { status: 200 });

  } catch (error: any) {
    console.error('Newsletter subscription API error:', error);

    // Handle unexpected errors
    return NextResponse.json(
      {
        success: false,
        message: '구독 처리 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.'
      },
      { status: 500 }
    );
  }
}

/**
 * GET /api/newsletter/subscribe
 * Returns API info (not used in production, just for debugging)
 */
export async function GET() {
  return NextResponse.json({
    endpoint: '/api/newsletter/subscribe',
    method: 'POST',
    description: 'Subscribe to NERDX APEC newsletter',
    parameters: {
      email: 'string (required)',
      firstName: 'string (optional)',
      source: 'footer | popup | checkout (optional, default: footer)'
    },
    response: {
      success: 'boolean',
      message: 'string',
      couponCode: 'string (if successful)'
    }
  });
}
