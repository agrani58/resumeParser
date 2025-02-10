from flask import Flask, request, jsonify
import stripe
from app.schema import create_connection
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Set Stripe secret key
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@app.route('/stripe-webhook', methods=['POST'])
def webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv("STRIPE_WEBHOOK_SECRET")
        )
    except ValueError:
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError:
        return jsonify({'error': 'Invalid signature'}), 400

    # Handle successful payment
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        try:
            with create_connection() as conn, conn.cursor() as cursor:
                # Update user subscription
                cursor.execute("""
                    UPDATE users 
                    SET subscription_type = 'premium' 
                    WHERE email = %s
                """, (session['customer_email'],))

                # Record payment
                cursor.execute("""
                    INSERT INTO payments 
                    (payment_id, customer_email, amount, currency, status, session_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    session['payment_intent'],
                    session['customer_email'],
                    session['amount_total'] / 100,
                    session['currency'].upper(),
                    session['payment_status'],
                    session['id']
                ))
                conn.commit()

            return jsonify({'success': True}), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return jsonify({'status': 'unhandled-event'}), 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)
