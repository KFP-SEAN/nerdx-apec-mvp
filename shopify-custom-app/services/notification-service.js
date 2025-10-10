/**
 * Notification Service
 * Handles email notifications for AR access unlock events
 * Uses Nodemailer with template support
 */

const nodemailer = require('nodemailer');
const logger = require('../utils/logger');
const { recordNotificationMetrics } = require('../utils/metrics');

// Email configuration
const SMTP_HOST = process.env.SMTP_HOST;
const SMTP_PORT = parseInt(process.env.SMTP_PORT) || 587;
const SMTP_SECURE = process.env.SMTP_SECURE === 'true';
const SMTP_USER = process.env.SMTP_USER;
const SMTP_PASSWORD = process.env.SMTP_PASSWORD;
const EMAIL_FROM = process.env.EMAIL_FROM || 'noreply@nerdx.com';
const EMAIL_FROM_NAME = process.env.EMAIL_FROM_NAME || 'NERDX APEC';
const AR_VIEWER_URL = process.env.AR_VIEWER_URL || 'https://ar.nerdx.com';

class NotificationService {
  constructor() {
    this.transporter = null;
    this.configured = false;
    this.initialize();
  }

  /**
   * Initialize email transporter
   */
  initialize() {
    if (!SMTP_HOST || !SMTP_USER || !SMTP_PASSWORD) {
      logger.warn('Email service not configured. Notifications will not be sent.');
      return;
    }

    try {
      this.transporter = nodemailer.createTransport({
        host: SMTP_HOST,
        port: SMTP_PORT,
        secure: SMTP_SECURE,
        auth: {
          user: SMTP_USER,
          pass: SMTP_PASSWORD,
        },
        pool: true, // Use connection pooling
        maxConnections: 5,
        maxMessages: 100,
      });

      this.configured = true;
      logger.info('Email notification service initialized', {
        host: SMTP_HOST,
        port: SMTP_PORT,
        secure: SMTP_SECURE,
      });

      // Verify connection
      this.verifyConnection();

    } catch (error) {
      logger.error('Failed to initialize email service:', error);
      this.configured = false;
    }
  }

  /**
   * Verify SMTP connection
   */
  async verifyConnection() {
    if (!this.transporter) {
      return false;
    }

    try {
      await this.transporter.verify();
      logger.info('Email service connection verified');
      return true;
    } catch (error) {
      logger.error('Email service connection verification failed:', error);
      return false;
    }
  }

  /**
   * Check if service is configured
   */
  isConfigured() {
    return this.configured && this.transporter !== null;
  }

  /**
   * Send AR access unlocked notification
   */
  async sendARUnlockedEmail(recipientData, tokenData) {
    if (!this.isConfigured()) {
      logger.warn('Email service not configured. Skipping notification.');
      return { sent: false, reason: 'not_configured' };
    }

    const startTime = Date.now();

    try {
      const { email, firstName, lastName } = recipientData;
      const { token, productId, productTitle, orderId } = tokenData;

      // Generate AR viewer URL with token
      const arViewerLink = `${AR_VIEWER_URL}?token=${token}&product=${productId}`;

      // Prepare email content
      const subject = `Your AR Experience is Now Available - ${productTitle || 'NERDX Product'}`;
      const htmlBody = this.generateARUnlockedHTML({
        firstName: firstName || 'Valued Customer',
        lastName,
        productTitle: productTitle || 'Your NERDX Product',
        arViewerLink,
        orderId,
        expiresAt: tokenData.expiresAt,
      });
      const textBody = this.generateARUnlockedText({
        firstName: firstName || 'Valued Customer',
        productTitle: productTitle || 'Your NERDX Product',
        arViewerLink,
        orderId,
        expiresAt: tokenData.expiresAt,
      });

      // Send email
      const info = await this.transporter.sendMail({
        from: `"${EMAIL_FROM_NAME}" <${EMAIL_FROM}>`,
        to: email,
        subject,
        text: textBody,
        html: htmlBody,
        headers: {
          'X-Entity-Ref-ID': orderId,
          'X-Product-ID': productId,
        },
      });

      const duration = (Date.now() - startTime) / 1000;
      recordNotificationMetrics.sent('ar_unlocked', 'success', duration);

      logger.notification('AR unlocked email sent', {
        email,
        orderId,
        productId,
        messageId: info.messageId,
      });

      return {
        sent: true,
        messageId: info.messageId,
        email,
        orderId,
        productId,
      };

    } catch (error) {
      const duration = (Date.now() - startTime) / 1000;
      recordNotificationMetrics.sent('ar_unlocked', 'error', duration);

      logger.error('Failed to send AR unlocked email:', error);
      return {
        sent: false,
        reason: 'send_error',
        error: error.message,
      };
    }
  }

  /**
   * Send AR access revoked notification
   */
  async sendARRevokedEmail(recipientData, productData, reason) {
    if (!this.isConfigured()) {
      logger.warn('Email service not configured. Skipping notification.');
      return { sent: false, reason: 'not_configured' };
    }

    const startTime = Date.now();

    try {
      const { email, firstName } = recipientData;
      const { productTitle, orderId } = productData;

      // Prepare email content
      const subject = `AR Access Update - ${productTitle || 'NERDX Product'}`;
      const htmlBody = this.generateARRevokedHTML({
        firstName: firstName || 'Valued Customer',
        productTitle: productTitle || 'Your NERDX Product',
        reason,
        orderId,
      });
      const textBody = this.generateARRevokedText({
        firstName: firstName || 'Valued Customer',
        productTitle: productTitle || 'Your NERDX Product',
        reason,
        orderId,
      });

      // Send email
      const info = await this.transporter.sendMail({
        from: `"${EMAIL_FROM_NAME}" <${EMAIL_FROM}>`,
        to: email,
        subject,
        text: textBody,
        html: htmlBody,
        headers: {
          'X-Entity-Ref-ID': orderId,
        },
      });

      const duration = (Date.now() - startTime) / 1000;
      recordNotificationMetrics.sent('ar_revoked', 'success', duration);

      logger.notification('AR revoked email sent', {
        email,
        orderId,
        messageId: info.messageId,
      });

      return {
        sent: true,
        messageId: info.messageId,
        email,
        orderId,
      };

    } catch (error) {
      const duration = (Date.now() - startTime) / 1000;
      recordNotificationMetrics.sent('ar_revoked', 'error', duration);

      logger.error('Failed to send AR revoked email:', error);
      return {
        sent: false,
        reason: 'send_error',
        error: error.message,
      };
    }
  }

  /**
   * Generate HTML email for AR unlocked notification
   */
  generateARUnlockedHTML(data) {
    return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your AR Experience is Ready</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: #ffffff;
            border-radius: 8px;
            padding: 40px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .logo {
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        }
        h1 {
            color: #2c3e50;
            font-size: 24px;
            margin-bottom: 20px;
        }
        .highlight {
            background-color: #e8f5e9;
            padding: 20px;
            border-radius: 6px;
            margin: 20px 0;
        }
        .cta-button {
            display: inline-block;
            background-color: #4CAF50;
            color: white;
            padding: 14px 28px;
            text-decoration: none;
            border-radius: 6px;
            font-weight: bold;
            margin: 20px 0;
            text-align: center;
        }
        .cta-button:hover {
            background-color: #45a049;
        }
        .info-box {
            background-color: #f9f9f9;
            padding: 15px;
            border-left: 4px solid #4CAF50;
            margin: 20px 0;
        }
        .footer {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            font-size: 12px;
            color: #666;
            text-align: center;
        }
        .order-info {
            font-size: 14px;
            color: #666;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">NERDX APEC</div>
        </div>

        <h1>Hi ${data.firstName},</h1>

        <p>Great news! Your AR experience for <strong>${data.productTitle}</strong> is now ready.</p>

        <div class="highlight">
            <p><strong>Experience your product in augmented reality!</strong></p>
            <p>Click the button below to launch the AR viewer and see your product come to life in your space.</p>
        </div>

        <center>
            <a href="${data.arViewerLink}" class="cta-button">Launch AR Experience</a>
        </center>

        <div class="info-box">
            <p><strong>What you can do:</strong></p>
            <ul>
                <li>View your product in 3D from any angle</li>
                <li>Place it in your real environment using AR</li>
                <li>Take photos and share with friends</li>
                <li>Explore detailed features and specifications</li>
            </ul>
        </div>

        <p><strong>Access Details:</strong></p>
        <ul>
            <li>Your AR access is valid for 90 days</li>
            <li>Expires on: ${new Date(data.expiresAt).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}</li>
            <li>Works on iOS and Android devices</li>
        </ul>

        <p>If you have any questions or need assistance, please don't hesitate to contact our support team.</p>

        <p>Enjoy your AR experience!</p>

        <p>Best regards,<br>The NERDX Team</p>

        <div class="order-info">
            Order #${data.orderId}
        </div>

        <div class="footer">
            <p>This email was sent to you because you recently purchased a product with AR capabilities from NERDX.</p>
            <p>&copy; ${new Date().getFullYear()} NERDX. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
    `;
  }

  /**
   * Generate plain text email for AR unlocked notification
   */
  generateARUnlockedText(data) {
    return `
Hi ${data.firstName},

Great news! Your AR experience for ${data.productTitle} is now ready.

LAUNCH YOUR AR EXPERIENCE:
${data.arViewerLink}

WHAT YOU CAN DO:
- View your product in 3D from any angle
- Place it in your real environment using AR
- Take photos and share with friends
- Explore detailed features and specifications

ACCESS DETAILS:
- Your AR access is valid for 90 days
- Expires on: ${new Date(data.expiresAt).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}
- Works on iOS and Android devices

If you have any questions or need assistance, please don't hesitate to contact our support team.

Enjoy your AR experience!

Best regards,
The NERDX Team

Order #${data.orderId}

---
This email was sent to you because you recently purchased a product with AR capabilities from NERDX.
© ${new Date().getFullYear()} NERDX. All rights reserved.
    `;
  }

  /**
   * Generate HTML email for AR revoked notification
   */
  generateARRevokedHTML(data) {
    const reasonText = data.reason === 'refund'
      ? 'Due to a refund processed for your order, your AR access has been deactivated.'
      : 'Your order was cancelled, and your AR access has been deactivated.';

    return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AR Access Update</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: #ffffff;
            border-radius: 8px;
            padding: 40px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .logo {
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        }
        h1 {
            color: #2c3e50;
            font-size: 24px;
            margin-bottom: 20px;
        }
        .notice {
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 20px;
            margin: 20px 0;
        }
        .footer {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            font-size: 12px;
            color: #666;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">NERDX APEC</div>
        </div>

        <h1>Hi ${data.firstName},</h1>

        <div class="notice">
            <p><strong>AR Access Update</strong></p>
            <p>${reasonText}</p>
        </div>

        <p>Product: <strong>${data.productTitle}</strong></p>
        <p>Order #${data.orderId}</p>

        <p>If you have any questions about this change, please contact our support team.</p>

        <p>Thank you for your understanding.</p>

        <p>Best regards,<br>The NERDX Team</p>

        <div class="footer">
            <p>&copy; ${new Date().getFullYear()} NERDX. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
    `;
  }

  /**
   * Generate plain text email for AR revoked notification
   */
  generateARRevokedText(data) {
    const reasonText = data.reason === 'refund'
      ? 'Due to a refund processed for your order, your AR access has been deactivated.'
      : 'Your order was cancelled, and your AR access has been deactivated.';

    return `
Hi ${data.firstName},

AR ACCESS UPDATE

${reasonText}

Product: ${data.productTitle}
Order #${data.orderId}

If you have any questions about this change, please contact our support team.

Thank you for your understanding.

Best regards,
The NERDX Team

---
© ${new Date().getFullYear()} NERDX. All rights reserved.
    `;
  }

  /**
   * Close transporter
   */
  async close() {
    if (this.transporter) {
      this.transporter.close();
      logger.info('Email notification service closed');
    }
  }
}

// Create singleton instance
const notificationService = new NotificationService();

module.exports = notificationService;
