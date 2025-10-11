import { NextRequest, NextResponse } from 'next/server';
import {
  findCustomerByEmail,
  createShopifyCustomer,
  addCustomerTags,
  updateCustomerMarketing,
  createDiscountCode,
} from '@/lib/shopify/admin';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { email, firstName, source } = body;

    // Validate email
    if (!email || typeof email !== 'string') {
      return NextResponse.json(
        { success: false, message: 'Email is required' },
        { status: 400 }
      );
    }

    const emailLower = email.toLowerCase().trim();

    // Check if customer exists
    let customer = await findCustomerByEmail(emailLower);

    if (customer) {
      // Customer exists - update marketing consent and add tag
      await updateCustomerMarketing(customer.id, true);

      // Add newsletter tag if not already present
      const tags = customer.tags || [];
      if (!tags.includes('newsletter-subscriber')) {
        await addCustomerTags(customer.id, ['newsletter-subscriber']);
      }

      console.log('Updated existing customer:', {
        id: customer.id,
        email: customer.email,
        tags: [...tags, 'newsletter-subscriber'],
      });
    } else {
      // Create new customer with marketing consent
      customer = await createShopifyCustomer({
        email: emailLower,
        firstName: firstName || 'Guest',
        lastName: 'Customer',
        acceptsMarketing: true,
        tags: ['newsletter-subscriber', 'web-signup'],
      });

      console.log('Created new customer for newsletter:', {
        id: customer.id,
        email: customer.email,
      });
    }

    // Create or verify welcome discount code exists
    const couponCode = 'WELCOME15';
    try {
      await createDiscountCode({
        code: couponCode,
        percentage: 15,
        usageLimit: 1,
      });
    } catch (error: any) {
      // If code already exists, that's fine
      if (!error.message?.includes('taken')) {
        console.error('Failed to create discount code:', error);
      }
    }

    return NextResponse.json(
      {
        success: true,
        message: '구독이 완료되었습니다! 🎉',
        couponCode,
        customer: {
          id: customer.id,
          email: customer.email,
        },
      },
      { status: 200 }
    );
  } catch (error: any) {
    console.error('Newsletter subscription error:', error);

    return NextResponse.json(
      {
        success: false,
        message:
          error.message ||
          '구독 처리 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.',
      },
      { status: 500 }
    );
  }
}
