"""
Stripe integration. Uses Stripe Checkout (hosted page) rather than
building a custom payment form - far less PCI surface area and less
code to maintain, which matters if this is meant to be low-maintenance.

Requires these env vars:
  STRIPE_SECRET_KEY       - from dashboard.stripe.com/apikeys
  STRIPE_PRICE_ID         - the recurring Price ID for your subscription product
  STRIPE_WEBHOOK_SECRET   - from the webhook endpoint you create in Stripe dashboard
"""
import stripe
from flask import Blueprint, request, jsonify, redirect, url_for, current_app
from flask_login import login_required, current_user

from app.models import db

billing_bp = Blueprint("billing", __name__)


@billing_bp.route("/billing/checkout", methods=["POST"])
@login_required
def create_checkout_session():
    stripe.api_key = current_app.config["STRIPE_SECRET_KEY"]

    if not current_user.stripe_customer_id:
        customer = stripe.Customer.create(email=current_user.email)
        current_user.stripe_customer_id = customer.id
        db.session.commit()

    session = stripe.checkout.Session.create(
        customer=current_user.stripe_customer_id,
        payment_method_types=["card"],
        mode="subscription",
        line_items=[{"price": current_app.config["STRIPE_PRICE_ID"], "quantity": 1}],
        success_url=url_for("pages.index", _external=True) + "?checkout=success",
        cancel_url=url_for("pages.index", _external=True) + "?checkout=cancelled",
    )
    return redirect(session.url, code=303)


@billing_bp.route("/billing/portal", methods=["POST"])
@login_required
def create_portal_session():
    """Lets a subscribed user manage/cancel their subscription without you building any UI for it."""
    stripe.api_key = current_app.config["STRIPE_SECRET_KEY"]
    session = stripe.billing_portal.Session.create(
        customer=current_user.stripe_customer_id,
        return_url=url_for("pages.index", _external=True),
    )
    return redirect(session.url, code=303)


@billing_bp.route("/billing/webhook", methods=["POST"])
def webhook():
    """
    Stripe calls this whenever a subscription is created/updated/cancelled.
    This is the source of truth for subscription_status - never trust the
    client to tell you whether it paid.
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

    from app.models import User

    obj = event["data"]["object"]
    event_type = event["type"]

    if event_type in ("customer.subscription.created", "customer.subscription.updated"):
        user = User.query.filter_by(stripe_customer_id=obj["customer"]).first()
        if user:
            user.stripe_subscription_id = obj["id"]
            user.subscription_status = "active" if obj["status"] == "active" else obj["status"]
            db.session.commit()

    elif event_type == "customer.subscription.deleted":
        user = User.query.filter_by(stripe_customer_id=obj["customer"]).first()
        if user:
            user.subscription_status = "canceled"
            db.session.commit()

    return jsonify({"received": True})
