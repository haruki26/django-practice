from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal

from utils.logger import get_logger

logger = get_logger(__name__)

QUANTIZE_UNIT = Decimal("0.01")
PERCENT_BASE = Decimal(100)


@dataclass(frozen=True)
class CustomerRecord:
    """Representation of a mock customer row."""

    customer_code: str
    customer_name: str
    customer_telno: str
    customer_postalcode: str
    customer_address: str
    discount_rate: int


@dataclass(frozen=True)
class CustomerSummary:
    """Aggregated order amount per customer."""

    customer_code: str
    customer_name: str
    total_amount: Decimal


@dataclass(frozen=True)
class ItemReportRow:
    """Aggregated order detail by item for a customer."""

    item_code: str
    item_name: str
    total_quantity: int
    unit_price: Decimal
    total_amount: Decimal


def get_customer(code: str = "C00001") -> CustomerRecord:
    """Return a single mock customer record."""
    logger.debug("Fetching mock customer", extra={"customer_code": code})
    return CustomerRecord(
        customer_code=code,
        customer_name="株式会社ウェルネスフーズ",
        customer_telno="03-1234-5678",
        customer_postalcode="100-0001",
        customer_address="東京都千代田区丸の内1-1-1",
        discount_rate=10,
    )


def get_customers() -> list[CustomerRecord]:
    """Return a list of mock customer records."""
    codes = ["C00001", "C00002", "C00003", "C00004", "C00005"]
    customers = [get_customer(code=code) for code in codes]
    logger.debug("Prepared %s mock customers", len(customers))
    return customers


def get_monthly_summary(year: int, month: int) -> tuple[list[CustomerSummary], Decimal]:
    """Return monthly mock aggregation and total."""
    base_amount = Decimal(520_000)
    multipliers = (Decimal(100), Decimal(85), Decimal(115), Decimal(95), Decimal(125))
    summaries = [
        CustomerSummary(
            customer_code=record.customer_code,
            customer_name=record.customer_name,
            total_amount=(base_amount * multiplier / PERCENT_BASE).quantize(QUANTIZE_UNIT),
        )
        for record, multiplier in zip(get_customers(), multipliers, strict=True)
    ]
    today = datetime.now(tz=UTC)
    scale_factor = Decimal(1)
    scale_factor += Decimal(year - today.year) * Decimal(2) / PERCENT_BASE
    scale_factor += Decimal(month - today.month) / PERCENT_BASE
    adjusted = [summary.total_amount * scale_factor for summary in summaries]
    total = sum(adjusted, start=Decimal(0))
    enriched = [
        CustomerSummary(
            customer_code=summary.customer_code,
            customer_name=summary.customer_name,
            total_amount=value.quantize(QUANTIZE_UNIT),
        )
        for summary, value in zip(summaries, adjusted, strict=True)
    ]
    logger.debug(
        "Built monthly summary",
        extra={"year": year, "month": month, "total": str(total)},
    )
    return enriched, total.quantize(QUANTIZE_UNIT)


def get_yearly_summary(year: int) -> tuple[list[CustomerSummary], Decimal]:
    """Return yearly mock aggregation and total."""
    monthly, _ = get_monthly_summary(year=year, month=6)
    annual_factor = Decimal(120) / PERCENT_BASE
    summaries = [
        CustomerSummary(
            customer_code=record.customer_code,
            customer_name=record.customer_name,
            total_amount=(record.total_amount * annual_factor).quantize(QUANTIZE_UNIT),
        )
        for record in monthly
    ]
    annual_total = sum((summary.total_amount for summary in summaries), start=Decimal(0))
    logger.debug("Built yearly summary", extra={"year": year, "total": str(annual_total)})
    return summaries, annual_total.quantize(QUANTIZE_UNIT)


def get_item_summary(customer_code: str) -> tuple[CustomerRecord, list[ItemReportRow], Decimal]:
    """Return order aggregation per item for the given customer."""
    customer = get_customer(code=customer_code)
    rows = [
        ItemReportRow(
            item_code="P1001",
            item_name="プロテインバー (ストロベリー)",
            total_quantity=120,
            unit_price=Decimal(280),
            total_amount=Decimal(33_600),
        ),
        ItemReportRow(
            item_code="P1002",
            item_name="プロテインバー (チョコレート)",
            total_quantity=96,
            unit_price=Decimal(280),
            total_amount=Decimal(26_880),
        ),
        ItemReportRow(
            item_code="P2001",
            item_name="ビタミンウォーター",
            total_quantity=150,
            unit_price=Decimal(150),
            total_amount=Decimal(22_500),
        ),
    ]
    total = sum((row.total_amount for row in rows), start=Decimal(0))
    logger.debug(
        "Built item summary",
        extra={"customer_code": customer_code, "item_count": len(rows), "total": str(total)},
    )
    return customer, rows, total.quantize(QUANTIZE_UNIT)


def sum_amount(rows: list[CustomerSummary | ItemReportRow]) -> Decimal:
    """Convenience function to sum total_amount columns."""
    total = sum((row.total_amount for row in rows), start=Decimal(0))
    return total.quantize(QUANTIZE_UNIT)
