from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseBilling(ABC):
    """
    Abstract billing interface.
    Allows swapping between Razorpay, Stripe, etc.
    """
    
    @abstractmethod
    async def create_subscription(
        self,
        user_id: str,
        plan_id: str,
        customer_email: str
    ) -> Dict[str, Any]:
        """
        Create a new subscription.
        
        Returns:
            {
                "subscription_id": str,
                "payment_url": str,  # For checkout
                "status": str
            }
        """
        pass
    
    @abstractmethod
    async def cancel_subscription(self, subscription_id: str) -> bool:
        """Cancel an existing subscription."""
        pass
    
    @abstractmethod
    async def get_subscription_status(self, subscription_id: str) -> str:
        """Get current subscription status."""
        pass
    
    @abstractmethod
    async def handle_webhook(self, payload: Dict[str, Any], signature: str) -> Dict[str, Any]:
        """
        Handle webhook from payment provider.
        
        Returns:
            {
                "event_type": str,
                "subscription_id": str,
                "status": str
            }
        """
        pass


class MockBilling(BaseBilling):
    """
    Mock billing adapter for development.
    Always returns success.
    """
    
    async def create_subscription(
        self,
        user_id: str,
        plan_id: str,
        customer_email: str
    ) -> Dict[str, Any]:
        return {
            "subscription_id": f"mock_sub_{user_id}",
            "payment_url": "https://mock-payment.com/checkout",
            "status": "active"
        }
    
    async def cancel_subscription(self, subscription_id: str) -> bool:
        return True
    
    async def get_subscription_status(self, subscription_id: str) -> str:
        return "active"
    
    async def handle_webhook(self, payload: Dict[str, Any], signature: str) -> Dict[str, Any]:
        return {
            "event_type": "subscription.activated",
            "subscription_id": payload.get("subscription_id", ""),
            "status": "active"
        }


def get_billing_adapter() -> BaseBilling:
    """
    Factory function to get billing adapter based on config.
    """
    from app.config import get_settings
    settings = get_settings()
    
    if settings.BILLING_PROVIDER == "razorpay":
        # TODO: Implement RazorpayBilling adapter
        return MockBilling()
    elif settings.BILLING_PROVIDER == "stripe":
        # TODO: Implement StripeBilling adapter
        return MockBilling()
    else:
        return MockBilling()
