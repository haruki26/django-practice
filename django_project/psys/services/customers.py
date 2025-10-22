from __future__ import annotations

from django.core.exceptions import ObjectDoesNotExist
from django.db import DatabaseError
from utils.logger import get_logger

from psys.models import Customer

logger = get_logger(__name__)


class CustomerServiceError(Exception):
    """Base exception for customer service failures."""

    def __init__(self, message: str) -> None:
        """Initialize the service error with a user-facing message."""
        super().__init__(message)


class CustomerNotFoundError(CustomerServiceError):
    """Raised when a customer could not be located by the provided criteria."""


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
    try:
        customer = Customer.objects.get(  # type: ignore[attr-defined]
            customer_code=customer_code,
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
