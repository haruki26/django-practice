from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from django.db import DatabaseError
from django.db.models import Sum
from utils.logger import get_logger

from psys.models import Customer, OrderDetails, Orders
from psys.services.customers import get_customer_by_code

logger = get_logger(__name__)


class ReportServiceError(Exception):
    """Raised when aggregation queries fail."""

    def __init__(self, message: str) -> None:
        """Store a user-facing error message."""
        super().__init__(message)


@dataclass(frozen=True)
class CustomerSummary:
    """Aggregated order amount per customer."""

    customer_code: str
    customer_name: str
    total_amount: Decimal


@dataclass(frozen=True)
class ItemReportRow:
    """Aggregated order detail per item."""

    item_code: str
    item_name: str
    total_quantity: int
    unit_price: Decimal
    total_amount: Decimal


def get_monthly_summary(year: int, month: int) -> tuple[list[CustomerSummary], Decimal]:
    """Return monthly order totals grouped by customer."""
    try:
        aggregates = (
            Orders.objects.filter(  # type: ignore[attr-defined]
                order_date__year=year,
                order_date__month=month,
                customer_code__delete_flag=0,
            )
            .values("customer_code", "customer_code__customer_name")
            .annotate(total_amount=Sum("total_price"))
            .order_by("customer_code")
        )
    except DatabaseError as exc:  # pragma: no cover - depends on database state
        logger.exception("Failed to build monthly summary", extra={"year": year, "month": month})
        message = "月次集計の取得に失敗しました。時間をおいて再度お試しください。"
        raise ReportServiceError(message) from exc

    summaries = [
        CustomerSummary(
            customer_code=row["customer_code"],
            customer_name=row["customer_code__customer_name"] or "",
            total_amount=Decimal(row["total_amount"] or 0),
        )
        for row in aggregates
    ]
    total = sum((entry.total_amount for entry in summaries), start=Decimal(0))
    return summaries, total


def get_yearly_summary(year: int) -> tuple[list[CustomerSummary], Decimal]:
    """Return yearly order totals grouped by customer."""
    try:
        aggregates = (
            Orders.objects.filter(  # type: ignore[attr-defined]
                order_date__year=year,
                customer_code__delete_flag=0,
            )
            .values("customer_code", "customer_code__customer_name")
            .annotate(total_amount=Sum("total_price"))
            .order_by("customer_code")
        )
    except DatabaseError as exc:  # pragma: no cover - depends on database state
        logger.exception("Failed to build yearly summary", extra={"year": year})
        message = "年次集計の取得に失敗しました。時間をおいて再度お試しください。"
        raise ReportServiceError(message) from exc

    summaries = [
        CustomerSummary(
            customer_code=row["customer_code"],
            customer_name=row["customer_code__customer_name"] or "",
            total_amount=Decimal(row["total_amount"] or 0),
        )
        for row in aggregates
    ]
    total = sum((entry.total_amount for entry in summaries), start=Decimal(0))
    return summaries, total


def get_item_summary(customer_code: str) -> tuple[Customer, list[ItemReportRow], Decimal]:
    """Return per-item totals for the specified customer."""
    customer = get_customer_by_code(customer_code=customer_code)

    try:
        aggregates = (
            OrderDetails.objects.filter(  # type: ignore[attr-defined]
                order_no__customer_code=customer,
            )
            .values("item_code", "item_code__item_name", "item_code__price")
            .annotate(
                total_quantity=Sum("order_num"),
                total_amount=Sum("order_price"),
            )
            .order_by("item_code")
        )
    except DatabaseError as exc:  # pragma: no cover - depends on database state
        logger.exception(
            "Failed to build item summary",
            extra={"customer_code": customer.customer_code},
        )
        message = "商品別集計の取得に失敗しました。時間をおいて再度お試しください。"
        raise ReportServiceError(message) from exc

    rows = [
        ItemReportRow(
            item_code=row["item_code"],
            item_name=row["item_code__item_name"] or "",
            total_quantity=int(row["total_quantity"] or 0),
            unit_price=Decimal(row["item_code__price"] or 0),
            total_amount=Decimal(row["total_amount"] or 0),
        )
        for row in aggregates
    ]
    total = sum((entry.total_amount for entry in rows), start=Decimal(0))
    return customer, rows, total
