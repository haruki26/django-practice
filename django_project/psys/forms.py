from __future__ import annotations

from django import forms

from psys.models import Employee
from psys.services.authentication import AuthenticationError, authenticate_employee


class EmployeeLoginForm(forms.Form):
    """Form used on the login screen."""

    employee_no = forms.CharField(
        label="従業員番号",
        max_length=6,
        min_length=4,
        widget=forms.TextInput(
            attrs={
                "placeholder": "例: EMP001",
                "data-auto-focus": "true",
                "inputmode": "text",
                "autocomplete": "username",
                "class": "form__input",
            },
        ),
    )
    password = forms.CharField(
        label="パスワード",
        max_length=12,
        min_length=4,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "パスワード",
                "autocomplete": "current-password",
                "class": "form__input",
            },
        ),
    )

    def clean(self) -> dict[str, object]:
        """Validate credentials against the employee master."""
        self._system_error = False
        cleaned_data = super().clean()
        employee_no = cleaned_data.get("employee_no")
        password = cleaned_data.get("password")
        if not employee_no or not password:
            return cleaned_data
        try:
            employee = authenticate_employee(
                employee_no=str(employee_no),
                password=str(password),
            )
        except AuthenticationError as error:
            self._system_error = error.is_system_error
            raise forms.ValidationError(str(error)) from error
        cleaned_data["employee"] = employee
        self._system_error = False
        return cleaned_data

    @property
    def employee(self) -> Employee | None:
        """Return the authenticated employee when validation succeeded."""
        employee = self.cleaned_data.get("employee")
        if isinstance(employee, Employee):
            return employee
        return None

    @property
    def has_system_error(self) -> bool:
        """Indicate whether the last validation failed due to a system error."""
        return getattr(self, "_system_error", False)


class CustomerSearchForm(forms.Form):
    """Form for finding a single customer by code."""

    customer_code = forms.CharField(
        label="得意先コード",
        max_length=6,
        min_length=3,
        widget=forms.TextInput(
            attrs={"placeholder": "例: C00001", "inputmode": "text", "class": "form__input"},
        ),
    )


class CustomerCodeForm(forms.Form):
    """Form that only requires a customer code."""

    customer_code = forms.CharField(
        label="得意先コード",
        max_length=6,
        min_length=3,
        widget=forms.TextInput(
            attrs={"placeholder": "例: C00001", "inputmode": "text", "class": "form__input"},
        ),
    )


class CustomerForm(forms.Form):
    """Form used for customer creation and updates."""

    customer_name = forms.CharField(
        label="得意先名",
        max_length=32,
        widget=forms.TextInput(attrs={"placeholder": "株式会社ウェルネス", "class": "form__input"}),
    )
    customer_telno = forms.CharField(
        label="電話番号",
        max_length=13,
        widget=forms.TextInput(
            attrs={"placeholder": "03-1234-5678", "inputmode": "tel", "class": "form__input"},
        ),
    )
    customer_postalcode = forms.CharField(
        label="郵便番号",
        max_length=8,
        widget=forms.TextInput(
            attrs={"placeholder": "100-0001", "inputmode": "numeric", "class": "form__input"},
        ),
    )
    customer_address = forms.CharField(
        label="住所",
        max_length=40,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": "東京都千代田区丸の内1-1-1",
                "class": "form__input",
            },
        ),
    )
    discount_rate = forms.IntegerField(
        label="割引率(%)",
        min_value=0,
        max_value=50,
        help_text="0〜50の範囲で入力してください。",
        widget=forms.NumberInput(attrs={"inputmode": "numeric", "class": "form__input"}),
    )


class MonthlyReportForm(forms.Form):
    """Form used on the monthly report screen."""

    year = forms.IntegerField(
        label="集計年",
        min_value=2015,
        max_value=2030,
        initial=2025,
        widget=forms.NumberInput(attrs={"inputmode": "numeric", "class": "form__input"}),
    )
    month = forms.IntegerField(
        label="集計月",
        min_value=1,
        max_value=12,
        initial=9,
        widget=forms.NumberInput(attrs={"inputmode": "numeric", "class": "form__input"}),
    )


class YearlyReportForm(forms.Form):
    """Form used on the yearly report screen."""

    year = forms.IntegerField(
        label="集計年",
        min_value=2015,
        max_value=2030,
        initial=2025,
        widget=forms.NumberInput(attrs={"inputmode": "numeric", "class": "form__input"}),
    )


class ItemReportForm(forms.Form):
    """Form used on the item report screen."""

    customer_code = forms.CharField(
        label="得意先コード",
        max_length=6,
        min_length=3,
        widget=forms.TextInput(
            attrs={"placeholder": "例: C00001", "inputmode": "text", "class": "form__input"},
        ),
    )
