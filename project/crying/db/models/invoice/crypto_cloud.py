import typing
from loguru import logger
from tortoise import fields

from project.crying.config import config
if typing.TYPE_CHECKING:
    from project.crying.db.models import User, SubscriptionTemplate

from .base import AbstractInvoice


class InvoiceCrypto(AbstractInvoice):
    """
    for create:
        amount
        shop_id
        order_id
        email
        currency

    result:
        {'status': 'success',
        'pay_url': 'https://cryptocloud.plus/pay/4N8RWT',
        'currency': 'BTC',
        'invoice_id': '4N8RWT',
        'amount': 3e-06,
        'amount_usd': 0.1170788818966779}
    check result:
        {'status': 'success', 'status_invoice': 'created'}
        {'status': 'success', 'status_invoice': 'paid'}
    checked time:
        7-10 m
    """
    user: "User" = fields.ForeignKeyField("models.User", on_delete=fields.CASCADE, related_name="invoice_cryptos")
    # shop_id = fields.CharField(50, default=config.merchants.crypto_cloud.shop_id)
    # todo L1 29.10.2022 1:54 taima:
    currency = fields.CharField(5, default="RUB", description="USD, RUB, EUR, GBP")
    order_id = fields.CharField(50, null=True, description="Custom product ID")

    async def check_payment(self) -> bool:
        return await config.merchants.crypto_cloud.is_paid(self.invoice_id)

    @classmethod
    async def create_invoice(
            cls,
            user: "User",
            subscription_template: "SubscriptionTemplate",
            amount: int | float | str,
            currency="RUB",
            email: str = None,
            order_id: str = None,
    ) -> "InvoiceCrypto":
        data = await config.merchants.crypto_cloud.create_invoice(
            amount=amount,
            currency=currency,
            order_id=order_id,
            email=email,
        )

        created_invoice = await cls.create(
            amount=amount,
            currency=currency,
            order_id=order_id,
            email=email,
            invoice_id=data["invoice_id"],
            pay_url=data["pay_url"],
            user=user,
            subscription_template=subscription_template,
        )

        logger.info(f"InvoiceCrypto created [{user.id}][{created_invoice.invoice_id}] {created_invoice.pay_url}")
        return created_invoice
