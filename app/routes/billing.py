"""
Monetization model: ads (see templates - ad slots) + pay-what-you-want
donations. No feature is gated behind payment - the whole point of a
civic info tool is that everyone gets the same access regardless of
whether they can pay.

Donations use Stripe Checkout in one-time payment mode with a
dynamically-priced line item (price_data), so the user picks their own
amount rather than choosing from preset tiers. No Stripe Product/Price
needs to be pre-created in the dashboard for this - it's built per-request.
"""
import stripe
from flask import Blueprint, request, jsonify, redirect, url_for, current_app
from flask_login import current_user

billing_bp = Blueprint("billing", __name__)

MIN_DONATION_CENTS = 100  # $1 floor - Stripe also has its own minimum (~$0.50 for USD)
MAX_DONATION_CENTS = 100000  # $1000 ceiling, sanity check against fat-fingered input


@billing_bp.route("/billing/donate", methods=["POST"])
def create_donation_checkout():
    stripe.api_key = current_app.config["STRIPE_SECRET_KEY"]

    try:
        amount_dollars = float(request.form.get("amount", "0"))
    except ValueError:
        return jsonify({"error": "invalid amount"}), 400

    amount_cents = round(amount_dollars * 100)
    if amount_cents < MIN_DONATION_CENTS or amount_cents > MAX_DONATION_CENTS:
        return jsonify({"error": f"amount must be between ${MIN_DONATION_CENTS/100:.2f} and ${MAX_DONATION_CENTS/100:.2f}"}), 400

    customer_email = current_user.email if current_user.is_authenticated else None

    session = stripe.checkout.Session.create(
        mode="payment",
        payment_method_types=["card"],
        customer_email=customer_email,
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {"name": "Who Represents Me - one-time support"},
                "unit_amount": amount_cents,
            },
            "quantity": 1,
        }],
        success_url=url_for("pages.index", _external=True) + "?donate=success",
        cancel_url=url_for("pages.index", _external=True) + "?donate=cancelled",
    )
    return redirect(session.url, code=303)


@billing_bp.route("/billing/webhook", methods=["POST"])
def webhook():
    """
    Records completed donations. Not required for the app to function -
    this is purely for your own records (e.g. a running total), since
    nothing in the app is gated on payment.
    """
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")
    stripe.api_key = current_app.config["STRIPE_SECRET_KEY"]

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, current_app.config["STRIPE_WEBHOOK_SECRET"]
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return jsonify({"error": "invalid signature"}), 400

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        amount_total = session.get("amount_total", 0)
        email = session.get("customer_email") or session.get("customer_details", {}).get("email")
        current_app.logger.info(f"Donation received: ${amount_total/100:.2f} from {email or 'anonymous'}")

    return jsonify({"received": True})
