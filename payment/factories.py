from abc import ABC, abstractmethod
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentProcessor(ABC):
    @abstractmethod
    def create_session(self, package_type, success_url, cancel_url, customer_email):
        pass


class StripePaymentProcessor(PaymentProcessor):
    def create_session(self, package_type, success_url, cancel_url, customer_email):
        if package_type == 'individual_use':
            amount = 100
        elif package_type == 'professional_use':
            amount = 999
        elif package_type == 'master_use':
            amount = 1499
        else:
            raise ValueError("Invalid package type")

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f'Video Library Access ({package_type})',
                    },
                    'unit_amount': amount,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            customer_email=customer_email,
        )
        return session


class PaymentProcessorFactory:
    @staticmethod
    def get_processor(processor_type):
        if processor_type == 'stripe':
            return StripePaymentProcessor()
        # poate mai tarziu adaugat paypal ?
        else:
            raise ValueError("Invalid processor type")
