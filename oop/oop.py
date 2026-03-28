from abc import ABC, abstractmethod


class LogMixin:
    def log(self, message: str):
        print(f"[{self.__class__.__name__}] {message}")


class PaymentProcessor(ABC):

    @abstractmethod
    def process(self, amount: float) -> bool: ...

    @abstractmethod
    def refund(self, amount: float) -> bool: ...

    def validate(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError(f"Amount must be positive, got {amount}")


class BaseProcessor(PaymentProcessor):

    def __init__(self, api_key: str, processing_charge: float):
        self.api_key = api_key
        self.processing_charge = processing_charge

    def process(self, amount: float) -> bool:
        self.validate(amount)
        total = amount + self.processing_charge
        print(f"{self.name}: charging ${total:.2f}")
        return True

    def refund(self, amount: float) -> bool:
        self.validate(amount)
        print(f"{self.name}: refunding ${amount:.2f}")
        return True


class StripeProcessor(BaseProcessor):
    name = "Stripe"


class PayPalProcessor(BaseProcessor):
    name = "PayPal"


class LoggedStripeProcessor(LogMixin, StripeProcessor):

    def process(self, amount: float) -> bool:
        self.log(f"charging ${amount + self.processing_charge:.2f}")
        return super().process(amount)

    def refund(self, amount: float) -> bool:
        self.log(f"refunding ${amount:.2f}")
        return super().refund(amount)


class PaymentService:
    def __init__(self, processor: PaymentProcessor):
        self.processor = processor

    def charge(self, amount: float) -> bool:
        return self.processor.process(amount)

    def refund(self, amount: float) -> bool:
        return self.processor.refund(amount)


service = PaymentService(LoggedStripeProcessor("sk_test", 0.6))
service.charge(23.4)
service.refund(10.0)