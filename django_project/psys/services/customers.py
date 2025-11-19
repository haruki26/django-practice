from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from django.core.exceptions import ObjectDoesNotExist
from django.db import DatabaseError, transaction
from utils.logger import get_logger

from psys.models import Customer

if TYPE_CHECKING:  # pragma: no cover - typing support only
    from django.db.models import QuerySet

logger = get_logger(__name__)


class CustomerServiceError(Exception):
    """Base exception for customer service failures."""

    def __init__(self, message: str) -> None:
        """Initialize the service error with a user-facing message."""
        super().__init__(message)


class CustomerNotFoundError(CustomerServiceError):
    """Raised when a customer could not be located by the provided criteria."""


@dataclass(frozen=True)
class CustomerPayload:
    """Normalized payload used for create and update operations."""

    customer_name: str
    customer_telno: str
    customer_postalcode: str
    customer_address: str
    discount_rate: int


CUSTOMER_CODE_PREFIX = "RA"


def _normalize_customer_code(customer_code: str) -> str:
    """Return an upper-case customer code suitable for database queries."""
    normalized = customer_code.strip().upper()
    if not normalized:
        message = "得意先コードを指定してください。"
        raise CustomerNotFoundError(message)
    return normalized


def list_active_customers() -> QuerySet[Customer]:
    """Return all active customers ordered by their code."""
    return Customer.objects.filter(delete_flag=0).order_by("customer_code")  # type: ignore[attr-defined]


def _generate_customer_code(prefix: str = CUSTOMER_CODE_PREFIX) -> str:
    """Generate a new sequential customer code.

    The caller is responsible for surrounding this function with a transaction
    to ensure the `SELECT ... FOR UPDATE` lock is effective.
    """
    last_code = (
        Customer.objects.select_for_update()  # type: ignore[attr-defined]
        .filter(customer_code__startswith=prefix)
        .order_by("-customer_code")
        .values_list("customer_code", flat=True)
        .first()
    )
    next_number = 1
    if last_code:
        suffix = last_code[len(prefix) :]
        if suffix.isdigit():
            next_number = int(suffix) + 1
    candidate = f"{prefix}{next_number:04d}"
    if Customer.objects.filter(customer_code=candidate).exists():  # type: ignore[attr-defined]
        logger.error("Generated duplicate customer code", extra={"customer_code": candidate})
        message = "得意先コードの採番に失敗しました。時間をおいて再度お試しください。"
        raise CustomerServiceError(message)
    return candidate


def create_customer(payload: CustomerPayload) -> Customer:
    """Create a new customer using the provided payload."""
    try:
        with transaction.atomic():
            customer_code = _generate_customer_code()
            customer = Customer.objects.create(  # type: ignore[attr-defined]
                customer_code=customer_code,
                customer_name=payload.customer_name,
                customer_telno=payload.customer_telno,
                customer_postalcode=payload.customer_postalcode,
                customer_address=payload.customer_address,
                discount_rate=payload.discount_rate,
                delete_flag=0,
            )
    except DatabaseError as exc:  # pragma: no cover - depends on database state
        logger.exception("Failed to create customer", extra={"customer_name": payload.customer_name})
        message = "得意先の登録に失敗しました。時間をおいて再度お試しください。"
        raise CustomerServiceError(message) from exc
    logger.info(
        "Customer created",
        extra={"customer_code": customer.customer_code, "customer_name": customer.customer_name},
    )
    return customer


def update_customer(customer_code: str, payload: CustomerPayload) -> Customer:
    """Update an existing customer with the supplied payload."""
    normalized_code = _normalize_customer_code(customer_code)
    try:
        with transaction.atomic():
            customer = get_customer_by_code(customer_code=normalized_code)
            customer.customer_name = payload.customer_name
            customer.customer_telno = payload.customer_telno
            customer.customer_postalcode = payload.customer_postalcode
            customer.customer_address = payload.customer_address
            customer.discount_rate = payload.discount_rate
            customer.save(
                update_fields=[
                    "customer_name",
                    "customer_telno",
                    "customer_postalcode",
                    "customer_address",
                    "discount_rate",
                ],
            )
    except CustomerNotFoundError:
        raise
    except DatabaseError as exc:  # pragma: no cover - depends on database state
        logger.exception(
            "Failed to update customer",
            extra={"customer_code": normalized_code},
        )
        message = "得意先の更新に失敗しました。時間をおいて再度お試しください。"
        raise CustomerServiceError(message) from exc
    logger.info("Customer updated", extra={"customer_code": normalized_code})
    return customer


def delete_customer(customer_code: str) -> Customer:
    """Mark the customer as deleted by setting the delete flag."""
    normalized_code = _normalize_customer_code(customer_code)
    try:
        with transaction.atomic():
            customer = get_customer_by_code(customer_code=normalized_code)
            customer.delete_flag = 1
            customer.save(update_fields=["delete_flag"])
    except CustomerNotFoundError:
        raise
    except DatabaseError as exc:  # pragma: no cover - depends on database state
        logger.exception("Failed to delete customer", extra={"customer_code": normalized_code})
        message = "得意先の削除に失敗しました。時間をおいて再度お試しください。"
        raise CustomerServiceError(message) from exc
    logger.info("Customer deleted", extra={"customer_code": normalized_code})
    return customer


def get_customer_by_code(customer_code: str) -> Customer:
    """Retrieve an active customer by its code.

    Args:
        customer_code: Identifier of the target customer.

    Returns:
        The matching customer model instance.

    Raises:
        CustomerNotFoundError: If the requested customer is not found.
        CustomerServiceError: If a database error occurs during retrieval.
    """
    normalized_code = _normalize_customer_code(customer_code)
    try:
        customer = Customer.objects.get(  # type: ignore[attr-defined]
            customer_code=normalized_code,
            delete_flag=0,
        )
    except ObjectDoesNotExist as exc:
        logger.info(
            "Customer not found",
            extra={"customer_code": customer_code},
        )
        message = "該当する得意先が存在しません。"
        raise CustomerNotFoundError(message) from exc
    except DatabaseError as exc:  # pragma: no cover - environment dependent
        logger.exception(
            "Database error while retrieving customer",
            extra={"customer_code": customer_code},
        )
        message = "得意先情報の取得中にエラーが発生しました。"
        raise CustomerServiceError(message) from exc

    logger.debug(
        "Customer retrieved",
        extra={"customer_code": customer.customer_code},
    )
    return customer
