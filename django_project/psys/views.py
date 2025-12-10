from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, cast

from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView, TemplateView
from django.views.generic.base import ContextMixin
from utils.logger import get_logger

from psys.services.customers import (
    CustomerNotFoundError,
    CustomerPayload,
    CustomerServiceError,
    create_customer,
    delete_customer,
    get_customer_by_code,
    list_active_customers,
    search_customers_by_name,
    update_customer,
)
from psys.services.reports import (
    ReportServiceError,
    get_item_summary,
    get_monthly_summary,
    get_yearly_summary,
)

from .forms import (
    CustomerForm,
    CustomerSearchForm,
    EmployeeLoginForm,
    ItemReportForm,
    MonthlyReportForm,
    YearlyReportForm,
)

logger = get_logger(__name__)

SESSION_KEY = "authenticated_employee"

if TYPE_CHECKING:
    from django.contrib.sessions.backends.base import SessionBase
    from django.forms import BaseForm
    from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
    from django.template.response import TemplateResponse

    from psys.models import Customer
else:  # pragma: no cover - runtime import not required
    SessionBase = object
    HttpRequest = object
    HttpResponse = object
    HttpResponseRedirect = object


def _get_session(request: HttpRequest) -> SessionBase:
    session_attr = getattr(request, "session", None)
    if session_attr is None:
        message = "Session middleware is required for this view."
        raise AttributeError(message)
    return cast("SessionBase", session_attr)


def _get_employee(request: HttpRequest) -> dict[str, str] | None:
    session = _get_session(request)
    employee = session.get(SESSION_KEY)
    if employee is None:
        return None
    return cast("dict[str, str]", employee)


class TemplateResponseFormView(TemplateView):
    """Form view variant that keeps rendering the template on success."""

    form_class: ClassVar[type[BaseForm] | None] = None
    initial: ClassVar[dict[str, Any]] = {}
    prefix: ClassVar[str | None] = None

    def get(self, _request: HttpRequest, *_args: object, **_kwargs: object) -> TemplateResponse:
        form = self.get_form()
        context = self.get_context_data(form=form)
        response = self.render_to_response(context)
        return cast("TemplateResponse", response)

    def post(self, _request: HttpRequest, *_args: object, **_kwargs: object) -> HttpResponse:
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def get_form_class(self) -> type[BaseForm]:
        form_class = self.form_class
        if form_class is None:
            message = f"{self.__class__.__name__} requires a form_class attribute or an override of get_form_class()."
            raise ImproperlyConfigured(message)
        return form_class

    def get_initial(self) -> dict[str, Any]:
        return self.initial.copy()

    def get_prefix(self) -> str | None:
        return self.prefix

    def get_form(self) -> BaseForm:
        form_class = self.get_form_class()
        return form_class(**self.get_form_kwargs())

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs: dict[str, Any] = {
            "initial": self.get_initial(),
            "prefix": self.get_prefix(),
        }
        if self.request.method in {"POST", "PUT"}:
            kwargs.update(
                {
                    "data": self.request.POST,
                    "files": self.request.FILES,
                },
            )
        return kwargs

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        context = super().get_context_data(**kwargs)
        if "form" not in context:
            context["form"] = self.get_form()
        return context

    def form_valid(self, form: BaseForm) -> TemplateResponse:
        context = self.get_context_data(form=form)
        response = self.render_to_response(context)
        return cast("TemplateResponse", response)

    def form_invalid(self, form: BaseForm) -> TemplateResponse:
        context = self.get_context_data(form=form)
        response = self.render_to_response(context)
        return cast("TemplateResponse", response)


class EmployeeSessionRequiredMixin(ContextMixin, View):
    """Mixin that ensures the employee session exists before access."""

    login_url = reverse_lazy("psys:login")

    def dispatch(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
        """Validate session and redirect to login when necessary."""
        session = _get_session(request)
        if SESSION_KEY not in session:
            messages.info(request, "先にログインしてください。")
            logger.info("Redirecting to login page", extra={"path": request.path})
            return redirect(self.login_url)
        response = super().dispatch(request, *args, **kwargs)
        return cast("HttpResponse", response)

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        """Inject logged-in employee information into the context."""
        context = super().get_context_data(**kwargs)
        context["employee"] = _get_employee(self.request)
        return context


class TopView(TemplateView):
    """Public top page that introduces the test environment."""

    template_name = "psys/top.html"

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        """Provide announcement messages for the top page."""
        context = super().get_context_data(**kwargs)
        context["announcements"] = [
            {
                "title": "販売支援システム テスト環境",
                "body": "得意先・受注データは MySQL 上の検証用データベースと連携しています。",
            },
            {
                "title": "開発ロードマップ",
                "body": "受注管理とオンライン販売機能を段階的に追加予定です。",
            },
            {
                "title": "データ更新について",
                "body": "登録・削除・集計の結果は即時に画面へ反映されます。",
            },
        ]
        context["employee"] = _get_employee(self.request)
        return context


class LoginView(FormView):
    """Form-based login that verifies employee credentials."""

    template_name = "psys/login.html"
    form_class = EmployeeLoginForm
    success_url = reverse_lazy("psys:main-menu")

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        """Include session information when returning to the login screen."""
        context = super().get_context_data(**kwargs)
        context["employee"] = _get_employee(self.request)
        return context

    def form_valid(self, form: EmployeeLoginForm) -> HttpResponseRedirect:
        """Persist the authenticated employee in the session."""
        employee = form.employee
        if employee is None:
            messages.error(self.request, "ログイン処理中にエラーが発生しました。時間をおいて再度お試しください。")
            logger.error(
                "Authenticated employee missing after form validation",
                extra={"employee_no": form.cleaned_data.get("employee_no", "")},
            )
            response = redirect("psys:login")
            return cast("HttpResponseRedirect", response)
        session = _get_session(self.request)
        session.cycle_key()
        session[SESSION_KEY] = {
            "employee_no": employee.employee_no,
            "employee_name": employee.employee_name or "",
        }
        messages.success(
            self.request,
            f"{employee.employee_name or employee.employee_no} さんでログインしました。メインメニューに移動します。",
        )
        logger.info("Employee login completed", extra={"employee_no": employee.employee_no})
        response = super().form_valid(form)
        return cast("HttpResponseRedirect", response)

    def form_invalid(self, form: EmployeeLoginForm) -> HttpResponse:
        """Log invalid attempts for traceability."""
        if form.has_system_error:
            messages.error(self.request, "ログイン処理中にエラーが発生しました。時間をおいて再度お試しください。")
        logger.warning("Login validation failed", extra={"errors": form.errors})
        return super().form_invalid(form)


class LogoutView(View):
    """Clear session information and return to the login page."""

    def post(self, request: HttpRequest, *_args: object, **_kwargs: object) -> HttpResponse:
        """Handle explicit logout via POST."""
        session = _get_session(request)
        session.pop(SESSION_KEY, None)
        messages.info(request, "ログアウトしました。")
        logger.info("Employee logout", extra={"path": request.path})
        return redirect("psys:login")

    def get(self, request: HttpRequest, *_args: object, **_kwargs: object) -> HttpResponse:
        """Allow GET access for convenience in the demo environment."""
        return self.post(request)


class MainMenuView(EmployeeSessionRequiredMixin, TemplateView):
    """Entry point after login that shows the primary navigation."""

    template_name = "psys/main_menu.html"

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        """Define cards for each business capability."""
        context = super().get_context_data(**kwargs)
        context["menu_items"] = [
            {
                "title": "得意先管理",
                "description": "得意先情報の検索・登録・更新を行います。",
                "url": reverse_lazy("psys:customer-menu"),
            },
            {
                "title": "受注管理",
                "description": "受注登録は今後のバージョンで提供予定です。",
                "url": "#",
                "disabled": True,
            },
            {
                "title": "得意先別集計",
                "description": "月次・年次・商品別の集計メニューを開きます。",
                "url": reverse_lazy("psys:reports-index"),
            },
        ]
        return context


class ReportsIndexView(EmployeeSessionRequiredMixin, TemplateView):
    """Landing page for the reports module that lists available summaries."""

    template_name = "psys/reports_index.html"

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        """Provide navigation cards for each aggregated report."""
        context = super().get_context_data(**kwargs)
        context["report_links"] = [
            {
                "title": "月別受注集計",
                "description": "指定した年月の受注を得意先別に集計します。",
                "url": reverse_lazy("psys:reports-monthly"),
            },
            {
                "title": "年次受注集計",
                "description": "指定年の受注状況を得意先別に確認します。",
                "url": reverse_lazy("psys:reports-yearly"),
            },
            {
                "title": "商品別受注集計",
                "description": "得意先ごとの商品別明細を表示します。",
                "url": reverse_lazy("psys:reports-by-item"),
            },
        ]
        return context


class CustomerMenuView(EmployeeSessionRequiredMixin, TemplateView):
    """Navigation menu dedicated to customer management operations."""

    template_name = "psys/customer_menu.html"

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        """Provide links to individual customer screens."""
        context = super().get_context_data(**kwargs)
        context["actions"] = [
            ("得意先検索", reverse_lazy("psys:customers-search")),
            ("得意先登録", reverse_lazy("psys:customers-create")),
            ("得意先削除", reverse_lazy("psys:customers-delete")),
            ("得意先変更", reverse_lazy("psys:customers-update-select")),
            ("得意先一覧", reverse_lazy("psys:customers-list")),
        ]
        return context


class CustomerUpdateSelectionView(EmployeeSessionRequiredMixin, TemplateView):
    """Intermediate screen for selecting the customer to edit."""

    template_name = "psys/customer_update_select.html"

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        """Provide active customers for selection before editing."""
        context = super().get_context_data(**kwargs)
        customers = list(list_active_customers())
        context["customers"] = customers
        context["has_customers"] = bool(customers)
        return context


class CustomerSearchView(EmployeeSessionRequiredMixin, TemplateResponseFormView):
    """Search page that shows customer details based on code."""

    template_name = "psys/customer_search.html"
    form_class = CustomerSearchForm

    def get_initial(self) -> dict[str, object]:
        initial = super().get_initial()
        code = str(self.request.GET.get("customer_code", "")).strip()
        name = str(self.request.GET.get("customer_name", "")).strip()
        if code:
            initial["customer_code"] = code
        if name:
            initial["customer_name"] = name
        return initial

    def get(self, request: HttpRequest, *args: object, **kwargs: object) -> TemplateResponse:
        customer_code = str(request.GET.get("customer_code", "")).strip()
        if customer_code:
            form = self.get_form()
            return self._search_by_code(cast("CustomerSearchForm", form), customer_code.upper())
        return super().get(request, *args, **kwargs)

    def form_valid(self, form: BaseForm) -> TemplateResponse:
        """Render the page with the matching customer from the database."""
        search_form = cast("CustomerSearchForm", form)
        customer_code = str(search_form.cleaned_data.get("customer_code", "")).upper()
        customer_name = str(search_form.cleaned_data.get("customer_name", "")).strip()
        if customer_code:
            return self._search_by_code(search_form, customer_code)
        return self._search_by_name(search_form, customer_name)

    def _search_by_code(self, form: CustomerSearchForm, customer_code: str) -> TemplateResponse:
        try:
            record = get_customer_by_code(customer_code=customer_code)
        except CustomerNotFoundError as error:
            form.add_error("customer_code", str(error))
            messages.warning(self.request, str(error))
            logger.info(
                "Customer search returned no results",
                extra={"customer_code": customer_code},
            )
            return cast("TemplateResponse", self.form_invalid(form))
        except CustomerServiceError as error:
            form.add_error(None, str(error))
            messages.error(self.request, str(error))
            logger.exception(
                "Customer search failed due to system error",
                extra={"customer_code": customer_code},
            )
            return cast("TemplateResponse", self.form_invalid(form))
        context = self.get_context_data(
            form=form,
            customer=record,
            update_url=reverse_lazy("psys:customers-update", kwargs={"customer_code": record.customer_code}),
        )
        messages.success(self.request, f"{record.customer_name} の情報を表示しています。")
        logger.info("Displayed customer", extra={"customer_code": customer_code})
        response = self.render_to_response(context)
        return cast("TemplateResponse", response)

    def _search_by_name(self, form: CustomerSearchForm, customer_name: str) -> TemplateResponse:
        try:
            records = search_customers_by_name(keyword=customer_name)
        except CustomerNotFoundError as error:
            form.add_error("customer_name", str(error))
            messages.warning(self.request, str(error))
            logger.info(
                "Customer name search returned no results",
                extra={"customer_name": customer_name},
            )
            return cast("TemplateResponse", self.form_invalid(form))
        except CustomerServiceError as error:
            form.add_error(None, str(error))
            messages.error(self.request, str(error))
            logger.exception(
                "Customer name search failed",
                extra={"customer_name": customer_name},
            )
            return cast("TemplateResponse", self.form_invalid(form))
        if len(records) == 1:
            record = records[0]
            context = self.get_context_data(
                form=form,
                customer=record,
                update_url=reverse_lazy("psys:customers-update", kwargs={"customer_code": record.customer_code}),
            )
            messages.success(self.request, f"{record.customer_name} の情報を表示しています。")
        else:
            context = self.get_context_data(form=form, customers=records)
            messages.success(
                self.request,
                f"{len(records)} 件の得意先が見つかりました。詳細を確認したい行を選択してください。",
            )
        logger.info(
            "Displayed customers by name",
            extra={"customer_name": customer_name, "hits": len(records)},
        )
        response = self.render_to_response(context)
        return cast("TemplateResponse", response)


class CustomerCreateView(EmployeeSessionRequiredMixin, TemplateResponseFormView):
    """Customer registration screen backed by MySQL."""

    template_name = "psys/customer_create.html"
    form_class = CustomerForm

    def form_valid(self, form: BaseForm) -> TemplateResponse:
        """Persist the new customer and display the saved record."""
        customer_form = cast("CustomerForm", form)
        payload = CustomerPayload(
            customer_name=customer_form.cleaned_data["customer_name"],
            customer_telno=customer_form.cleaned_data["customer_telno"],
            customer_postalcode=customer_form.cleaned_data["customer_postalcode"],
            customer_address=customer_form.cleaned_data["customer_address"],
            discount_rate=customer_form.cleaned_data["discount_rate"],
        )
        try:
            record = create_customer(payload=payload)
        except CustomerServiceError as error:
            customer_form.add_error(None, str(error))
            messages.error(self.request, str(error))
            logger.warning("Customer registration failed", extra={"errors": customer_form.errors})
            return cast("TemplateResponse", self.form_invalid(customer_form))
        context = self.get_context_data(form=customer_form, customer=record)
        messages.success(self.request, f"得意先コード {record.customer_code} を登録しました。")
        logger.info("Customer registered", extra={"customer_code": record.customer_code})
        response = self.render_to_response(context)
        return cast("TemplateResponse", response)


class CustomerDeleteSelectionView(EmployeeSessionRequiredMixin, TemplateView):
    """List view for choosing which customer to delete."""

    template_name = "psys/customer_delete_select.html"

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        """Provide active customers so the user can choose one to delete."""
        context = super().get_context_data(**kwargs)
        customers = list(list_active_customers())
        context["customers"] = customers
        context["has_customers"] = bool(customers)
        return context


class CustomerDeleteConfirmView(EmployeeSessionRequiredMixin, TemplateView):
    """Confirmation screen for deleting a specific customer."""

    template_name = "psys/customer_delete.html"

    def dispatch(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
        """Ensure the target customer exists before showing the confirmation."""
        try:
            self._customer_cache = self._get_customer()
        except CustomerNotFoundError as error:
            messages.warning(request, str(error))
            logger.info(
                "Customer delete confirmation target missing",
                extra={"customer_code": kwargs.get("customer_code", "")},
            )
            return redirect("psys:customers-delete")
        except CustomerServiceError as error:
            messages.error(request, str(error))
            logger.exception("Customer lookup failed during delete confirmation")
            return redirect("psys:customer-menu")
        return super().dispatch(request, *args, **kwargs)

    def _get_customer_code(self) -> str:
        code = str(self.kwargs.get("customer_code", "")).strip().upper()
        if not code:
            message = "得意先コードが指定されていません。"
            raise CustomerNotFoundError(message)
        return code

    def _get_customer(self) -> Customer:
        if hasattr(self, "_customer_cache"):
            return cast("Customer", self._customer_cache)
        code = self._get_customer_code()
        customer = get_customer_by_code(customer_code=code)
        self._customer_cache = customer
        return customer

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        """Provide the customer details for the confirmation template."""
        context = super().get_context_data(**kwargs)
        context.setdefault("customer", self._get_customer())
        return context

    def post(self, request: HttpRequest, *_args: object, **_kwargs: object) -> HttpResponse:
        """Delete the customer after confirmation and return to the selection list."""
        customer_code = self._get_customer_code()
        try:
            record = delete_customer(customer_code=customer_code)
        except CustomerNotFoundError as error:
            messages.warning(request, str(error))
            logger.info("Customer deletion target not found on confirmation", extra={"customer_code": customer_code})
            return redirect("psys:customers-delete")
        except CustomerServiceError as error:
            messages.error(request, str(error))
            logger.exception("Customer deletion failed", extra={"customer_code": customer_code})
            return redirect("psys:customers-delete")
        messages.success(request, f"{record.customer_name} を削除しました。")
        logger.info("Customer deleted", extra={"customer_code": customer_code})
        return redirect("psys:customers-delete")


class CustomerUpdateView(EmployeeSessionRequiredMixin, TemplateResponseFormView):
    """Customer update screen."""

    template_name = "psys/customer_update.html"
    form_class = CustomerForm

    def dispatch(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
        """Ensure the target customer exists before continuing."""
        try:
            self._customer_cache = self._get_customer()
        except CustomerNotFoundError as error:
            messages.error(request, str(error))
            response = redirect("psys:customers-search")
            return cast("HttpResponse", response)
        except CustomerServiceError as error:
            messages.error(request, str(error))
            response = redirect("psys:customer-menu")
            return cast("HttpResponse", response)
        return super().dispatch(request, *args, **kwargs)

    def _get_customer_code(self) -> str:
        code = str(self.kwargs.get("customer_code", "")).strip().upper()
        if not code:
            message = "得意先コードが指定されていません。"
            raise CustomerNotFoundError(message)
        return code

    def _get_customer(self) -> Customer:
        if hasattr(self, "_customer_cache"):
            return cast("Customer", self._customer_cache)
        code = self._get_customer_code()
        customer = get_customer_by_code(customer_code=code)
        self._customer_cache = customer
        return customer

    def get_initial(self) -> dict[str, object]:
        """Populate the form with the current database values."""
        record = self._get_customer()
        return {
            "customer_name": record.customer_name,
            "customer_telno": record.customer_telno,
            "customer_postalcode": record.customer_postalcode,
            "customer_address": record.customer_address,
            "discount_rate": record.discount_rate,
        }

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        """Include the current customer for preview on initial display."""
        context = super().get_context_data(**kwargs)
        context.setdefault("customer", self._get_customer())
        return context

    def form_valid(self, form: BaseForm) -> TemplateResponse:
        """Persist the updated values and show the result."""
        customer_form = cast("CustomerForm", form)
        payload = CustomerPayload(
            customer_name=customer_form.cleaned_data["customer_name"],
            customer_telno=customer_form.cleaned_data["customer_telno"],
            customer_postalcode=customer_form.cleaned_data["customer_postalcode"],
            customer_address=customer_form.cleaned_data["customer_address"],
            discount_rate=customer_form.cleaned_data["discount_rate"],
        )
        customer_code = self._get_customer_code()
        try:
            record = update_customer(customer_code=customer_code, payload=payload)
        except CustomerNotFoundError as error:
            customer_form.add_error(None, str(error))
            messages.warning(self.request, str(error))
            logger.info("Customer update target missing", extra={"customer_code": customer_code})
            return cast("TemplateResponse", self.form_invalid(customer_form))
        except CustomerServiceError as error:
            customer_form.add_error(None, str(error))
            messages.error(self.request, str(error))
            logger.exception("Customer update failed", extra={"customer_code": customer_code})
            return cast("TemplateResponse", self.form_invalid(customer_form))
        self._customer_cache = record
        context = self.get_context_data(form=customer_form, customer=record)
        messages.success(self.request, f"{record.customer_name} の情報を更新しました。")
        logger.info("Customer updated", extra={"customer_code": customer_code})
        response = self.render_to_response(context)
        return cast("TemplateResponse", response)


class CustomerListView(EmployeeSessionRequiredMixin, TemplateView):
    """Simple list of registered customers."""

    template_name = "psys/customer_list.html"

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        """Provide all active customers to the template."""
        context = super().get_context_data(**kwargs)
        customers = list(list_active_customers())
        context["customers"] = customers
        context["has_customers"] = bool(customers)
        return context


class MonthlyReportView(EmployeeSessionRequiredMixin, TemplateResponseFormView):
    """Monthly aggregation screen."""

    template_name = "psys/reports_monthly.html"
    form_class = MonthlyReportForm

    def form_valid(self, form: BaseForm) -> TemplateResponse:
        """Display aggregated amounts per customer for the selected month."""
        monthly_form = cast("MonthlyReportForm", form)
        year = monthly_form.cleaned_data["year"]
        month = monthly_form.cleaned_data["month"]
        try:
            summaries, total = get_monthly_summary(year=year, month=month)
        except ReportServiceError as error:
            monthly_form.add_error(None, str(error))
            messages.error(self.request, str(error))
            logger.exception("Monthly report failed", extra={"year": year, "month": month})
            return cast("TemplateResponse", self.form_invalid(monthly_form))
        context = self.get_context_data(form=monthly_form, summaries=summaries, total=total)
        messages.success(self.request, f"{year}年{month}月の集計結果を表示しています。")
        logger.info("Monthly report displayed", extra={"year": year, "month": month})
        response = self.render_to_response(context)
        return cast("TemplateResponse", response)


class YearlyReportView(EmployeeSessionRequiredMixin, TemplateResponseFormView):
    """Yearly aggregation screen."""

    template_name = "psys/reports_yearly.html"
    form_class = YearlyReportForm

    def form_valid(self, form: BaseForm) -> TemplateResponse:
        """Display aggregated amounts per customer for the selected year."""
        yearly_form = cast("YearlyReportForm", form)
        year = yearly_form.cleaned_data["year"]
        try:
            summaries, total = get_yearly_summary(year=year)
        except ReportServiceError as error:
            yearly_form.add_error(None, str(error))
            messages.error(self.request, str(error))
            logger.exception("Yearly report failed", extra={"year": year})
            return cast("TemplateResponse", self.form_invalid(yearly_form))
        context = self.get_context_data(form=yearly_form, summaries=summaries, total=total)
        messages.success(self.request, f"{year}年の集計結果を表示しています。")
        logger.info("Yearly report displayed", extra={"year": year})
        response = self.render_to_response(context)
        return cast("TemplateResponse", response)


class ItemReportView(EmployeeSessionRequiredMixin, TemplateResponseFormView):
    """Item-based aggregation screen."""

    template_name = "psys/reports_by_item.html"
    form_class = ItemReportForm

    def form_valid(self, form: BaseForm) -> TemplateResponse:
        """Display item level aggregation for the specified customer."""
        item_form = cast("ItemReportForm", form)
        customer_code = item_form.cleaned_data["customer_code"].upper()
        try:
            customer, rows, total = get_item_summary(customer_code=customer_code)
        except CustomerNotFoundError as error:
            item_form.add_error("customer_code", str(error))
            messages.warning(self.request, str(error))
            logger.info("Item report customer missing", extra={"customer_code": customer_code})
            return cast("TemplateResponse", self.form_invalid(item_form))
        except CustomerServiceError as error:
            item_form.add_error(None, str(error))
            messages.error(self.request, str(error))
            logger.exception("Item report customer lookup failed", extra={"customer_code": customer_code})
            return cast("TemplateResponse", self.form_invalid(item_form))
        except ReportServiceError as error:
            item_form.add_error(None, str(error))
            messages.error(self.request, str(error))
            logger.exception("Item report aggregation failed", extra={"customer_code": customer_code})
            return cast("TemplateResponse", self.form_invalid(item_form))
        context = self.get_context_data(form=item_form, customer=customer, rows=rows, total=total)
        messages.success(self.request, f"{customer.customer_name} の商品別集計を表示しています。")
        logger.info("Item report displayed", extra={"customer_code": customer_code})
        response = self.render_to_response(context)
        return cast("TemplateResponse", response)
