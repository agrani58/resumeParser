
from datetime import timezone
import stripe
import os
import streamlit as st
from datetime import datetime as dt, timedelta, timezone

from app.schema import get_connection

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def create_checkout_session(email: str):
    try:
        return stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': 'price_1QqzjsD1iUPBafNcjG7nN4pM',
                'quantity': 1,
            }],
            mode='subscription',
            success_url=os.getenv("BASE_URL") + "?payment=success",
            cancel_url=os.getenv("BASE_URL") + "?payment=cancel",
            customer_email=email,  
            subscription_data={
                'metadata': {'user_email': email}  
            }
        ).url
    except Exception as e:
        st.error(f"Payment error: {e}")
        return None
def check_subscription(email):
    try:
        with get_connection() as conn:
            with conn.cursor(buffered=True) as cursor:
                cursor.execute("""
                    SELECT 
                        subscription_type, 
                        end_date, 
                        is_active 
                    FROM subscriptions 
                    WHERE email = %s 
                    ORDER BY end_date DESC 
                    LIMIT 1
                """, (email,))
                subscription = cursor.fetchone()
                
                if not subscription:
                    return False  
                
                subscription_type, end_date, is_active = subscription
                current_time = dt.now(timezone.utc)
                
                if subscription_type == 'free' and current_time > end_date:
                    return False  
                elif subscription_type == 'premium' and (not is_active or current_time > end_date):
                    return False  
                
                return True 
    except Exception as e:
        st.error(f"Subscription check error: {e}")
        return False
    
    #handling payment after doing the sub payment
def handle_payment_success(email):

    try:
       
        if not email:
            st.error("Payment failed: User email is missing.")
            return False

        # Debug  Confirm email is captured
        st.write(f"Debug: Updating subscriptions for email '{email}'")

        with get_connection() as conn:
            with conn.cursor() as cursor:
        
                cursor.execute("""
                    UPDATE subscriptions 
                    SET is_active = FALSE 
                    WHERE email = %s
                """, (email,))
                
                
                start_date = dt.now(timezone.utc)
                end_date = start_date + timedelta(days=30)
                
                cursor.execute("""
                    INSERT INTO subscriptions 
                    (email, subscription_type, start_date, end_date, is_active)
                    VALUES (%s, 'premium', %s, %s, TRUE)
                """, (email, start_date, end_date))
                
                conn.commit()
                st.success("Premium subscription activated!")
                return True
    except Exception as e:
        st.error(f"Payment processing failed: {str(e)}")
        return False