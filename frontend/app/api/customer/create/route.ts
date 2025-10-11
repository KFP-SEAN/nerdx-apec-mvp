import { NextRequest, NextResponse } from 'next/server';
import {
  createShopifyCustomer,
  findCustomerByEmail,
} from '@/lib/shopify/admin';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { email, firstName, lastName, phone, acceptsMarketing } = body;

    // Validate required fields
    if (!email || !firstName || !lastName) {
      return NextResponse.json(
        {
          success: false,
          message: 'Email, first name, and last name are required',
        },
        { status: 400 }
      );
    }

    // Check if customer already exists
    const existingCustomer = await findCustomerByEmail(email);
    if (existingCustomer) {
      return NextResponse.json(
        {
          success: false,
          message: 'An account with this email already exists',
          alreadyExists: true,
        },
        { status: 409 }
      );
    }

    // Create customer in Shopify
    const customer = await createShopifyCustomer({
      email,
      firstName,
      lastName,
      phone,
      acceptsMarketing: acceptsMarketing || false,
      tags: ['web-signup'],
    });

    console.log('Customer created in Shopify:', {
      id: customer.id,
      email: customer.email,
    });

    return NextResponse.json(
      {
        success: true,
        customer: {
          id: customer.id,
          email: customer.email,
          firstName: customer.firstName,
          lastName: customer.lastName,
          phone: customer.phone,
          acceptsMarketing: customer.acceptsMarketing,
        },
      },
      { status: 201 }
    );
  } catch (error: any) {
    console.error('Customer creation error:', error);

    return NextResponse.json(
      {
        success: false,
        message:
          error.message ||
          'Failed to create customer. Please try again later.',
      },
      { status: 500 }
    );
  }
}
