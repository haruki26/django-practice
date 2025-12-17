from __future__ import annotations

from django.core.exceptions import ObjectDoesNotExist
from django.db import DatabaseError
from utils.logger import get_logger

from psys.models import Employee

logger = get_logger(__name__)


class AuthenticationError(Exception):
    """Raised when employee authentication fails."""

    def __init__(self, message: str, *, is_system_error: bool = False) -> None:
        """Initialize the authentication error.

        Args:
            message: Explanation of the failure.
            is_system_error: Indicates whether the failure was caused by a system issue.
        """
        super().__init__(message)
        self.is_system_error = is_system_error


def authenticate_employee(employee_no: str, password: str) -> Employee:
    """Validate employee credentials and return the matching employee.

    Args:
        employee_no: Identifier of the employee attempting to log in.
        password: Plain text password provided by the employee.

    Returns:
        The authenticated employee instance.

    Raises:
        AuthenticationError: If the credentials are invalid or a system error occurs.
    """
    try:
        employee = Employee.objects.get(employee_no=employee_no)
    except ObjectDoesNotExist as exc:
        logger.info(
            "Employee not found during authentication",
            extra={"employee_no": employee_no},
        )
        message = "従業員番号またはパスワードが正しくありません。"
        raise AuthenticationError(message) from exc
    except DatabaseError as exc:
        logger.exception(
            "Database error while fetching employee",
            extra={"employee_no": employee_no},
        )
        message = "ログイン処理中にエラーが発生しました。"
        raise AuthenticationError(message, is_system_error=True) from exc

    stored_password = employee.password or ""
    if stored_password != password:
        logger.info(
            "Password mismatch during authentication",
            extra={"employee_no": employee_no},
        )
        message = "従業員番号またはパスワードが正しくありません。"
        raise AuthenticationError(message)

    return employee
