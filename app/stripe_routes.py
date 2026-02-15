"""Stripe integration for payments and subscriptions."""

import stripe
from fastapi import APIRouter, HTTPException, status, Request, Header
from fastapi.responses import JSONResponse

from app.config import settings

router = APIRouter(prefix="/stripe", tags=["payments"])

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


@router.post("/create-checkout-session")
async def create_checkout_session(tier: str = "hobby"):
    """Create a Stripe Checkout session for subscription."""
    if not settings.STRIPE_SECRET_KEY or "placeholder" in settings.STRIPE_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe not configured"
        )
    
    price_map = {
        "hobby": settings.STRIPE_PRICE_HOBBY,
        "pro": settings.STRIPE_PRICE_PRO,
    }
    
    price_id = price_map.get(tier)
    if not price_id or "placeholder" in price_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid tier or price not configured: {tier}"
        )
    
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price": price_id,
                "quantity": 1,
            }],
            mode="subscription",
            success_url=f"{settings.FRONTEND_URL}/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.FRONTEND_URL}/cancel",
        )
        return {"checkout_url": session.url, "session_id": session.id}
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None, alias="Stripe-Signature")):
    """Handle Stripe webhooks for subscription events."""
    if not settings.STRIPE_WEBHOOK_SECRET or "placeholder" in settings.STRIPE_WEBHOOK_SECRET:
        # In development, just log and return success
        payload = await request.body()
        print(f"⚠️  Stripe webhook received but not configured. Payload: {payload[:200]}...")
        return {"status": "ignored", "reason": "webhook_secret_not_configured"}
    
    payload = await request.body()
    
    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle events
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        print(f"✅ Checkout completed: {session['id']}")
        # TODO: Update user tier in database
        
    elif event["type"] == "invoice.paid":
        invoice = event["data"]["object"]
        print(f"✅ Invoice paid: {invoice['id']}")
        # TODO: Update subscription status
        
    elif event["type"] == "invoice.payment_failed":
        invoice = event["data"]["object"]
        print(f"❌ Payment failed: {invoice['id']}")
        # TODO: Notify user and downgrade tier
        
    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        print(f"🗑️  Subscription cancelled: {subscription['id']}")
        # TODO: Downgrade user to free tier
    
    return {"status": "success"}


@router.get("/config")
async def get_stripe_config():
    """Get public Stripe configuration."""
    return {
        "publishable_key": settings.STRIPE_SECRET_KEY[:7] + "..." if settings.STRIPE_SECRET_KEY else None,
        "prices": {
            "hobby": settings.STRIPE_PRICE_HOBBY if settings.STRIPE_PRICE_HOBBY else None,
            "pro": settings.STRIPE_PRICE_PRO if settings.STRIPE_PRICE_PRO else None,
        }
    }
