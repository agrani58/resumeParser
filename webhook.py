import sys
import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify
import stripe
from dotenv import load_dotenv

# Configure path
project_root = os.path.dirname(os.path.abspath("ResumeParser/webhook.py"))  
sys.path.append("ResumeParser")
from app.schema import create_connection

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/stripe-webhook', methods=['POST'])
def webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv("STRIPE_WEBHOOK_SECRET")
        )
    except ValueError as e:
        logger.error(f"Invalid payload: {str(e)}")
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {str(e)}")
        return jsonify({'error': 'Invalid signature'}), 400

    # Handle successful checkout session
    if event['type'] == 'checkout.session.completed':
        return handle_checkout_session(event['data']['object'])

    logger.info(f"Unhandled event type: {event['type']}")
    return jsonify({'status': 'unhandled-event'}), 200

def handle_checkout_session(session):
    try:
        # Retrieve subscription details
        subscription = stripe.Subscription.retrieve(session.subscription)
        customer_email = session.customer_email
        
        # Calculate subscription dates
        start_date = datetime.utcfromtimestamp(subscription.current_period_start)
        end_date = datetime.utcfromtimestamp(subscription.current_period_end)

        with create_connection() as conn, conn.cursor() as cursor:
            # Update users table
            cursor.execute("""
                UPDATE users 
                SET subscription_type = 'premium' 
                WHERE email = %s
            """, (customer_email,))

            # Create/update subscription
            cursor.execute("""
                INSERT INTO subscriptions 
                (email, subscription_type, start_date, end_date, is_active)
                VALUES (%s, 'premium', %s, %s, TRUE)
                ON DUPLICATE KEY UPDATE
                subscription_type = 'premium',
                start_date = VALUES(start_date),
                end_date = VALUES(end_date),
                is_active = TRUE
            """, (customer_email, start_date, end_date))

            # Record payment
            cursor.execute("""
                INSERT INTO payments 
                (payment_id, customer_email, amount, currency, status, session_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                session.payment_intent,
                customer_email,
                session.amount_total / 100,
                session.currency.upper(),
                session.payment_status,
                session.id
            ))

            conn.commit()
            logger.info(f"Processed new subscription for {customer_email}")
            return jsonify({'success': True}), 200

    except Exception as e:
        logger.error(f"Error handling checkout: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)