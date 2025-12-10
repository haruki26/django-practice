from __future__ import annotations

from django.urls import path

from . import views

app_name = "psys"

urlpatterns = [
    path("", views.TopView.as_view(), name="top"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("menu/", views.MainMenuView.as_view(), name="main-menu"),
    path("customers/menu/", views.CustomerMenuView.as_view(), name="customer-menu"),
    path("customers/search/", views.CustomerSearchView.as_view(), name="customers-search"),
    path("customers/new/", views.CustomerCreateView.as_view(), name="customers-create"),
    path("customers/delete/", views.CustomerDeleteSelectionView.as_view(), name="customers-delete"),
    path(
        "customers/<str:customer_code>/delete/",
        views.CustomerDeleteConfirmView.as_view(),
        name="customers-delete-confirm",
    ),
    path("customers/update/", views.CustomerUpdateSelectionView.as_view(), name="customers-update-select"),
    path(
        "customers/<str:customer_code>/edit/",
        views.CustomerUpdateView.as_view(),
        name="customers-update",
    ),
    path("customers/list/", views.CustomerListView.as_view(), name="customers-list"),
    path("reports/", views.ReportsIndexView.as_view(), name="reports-index"),
    path("reports/monthly/", views.MonthlyReportView.as_view(), name="reports-monthly"),
    path("reports/yearly/", views.YearlyReportView.as_view(), name="reports-yearly"),
    path("reports/by-item/", views.ItemReportView.as_view(), name="reports-by-item"),
]
