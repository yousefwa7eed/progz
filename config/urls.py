from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from apps.accounts import views as accounts_views
from apps.reports import views as reports_views
from apps.beneficiaries import views as beneficiaries_views
from apps.donors import views as donors_views
from apps.donations import views as donations_views
from apps.sponsorships import views as sponsorships_views
from apps.cases import views as cases_views
from apps.projects import views as projects_views
from apps.finance import views as finance_views
from apps.inventory import views as inventory_views
from apps.employees import views as employees_views
from apps.communications import views as communications_views
from apps.occasions import views as occasions_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth
    path('login/', accounts_views.login_view, name='login'),
    path('logout/', accounts_views.logout_view, name='logout'),
    path('register/', accounts_views.register_view, name='register'),
    path('profile/', accounts_views.profile_view, name='profile'),
    path('change-password/', accounts_views.change_password_view, name='change_password'),
    path('users/', accounts_views.users_list_view, name='users_list'),
    path('users/<uuid:user_id>/toggle-active/', accounts_views.user_toggle_active_view, name='user_toggle_active'),
    path('activity/', accounts_views.activity_log_view, name='activity_log'),

    # Dashboard
    path('', accounts_views.dashboard_view, name='dashboard'),
    path('dashboard/', accounts_views.dashboard_view, name='dashboard'),

    # Beneficiaries
    path('beneficiaries/', beneficiaries_views.BeneficiaryListView.as_view(), name='beneficiary_list'),
    path('beneficiaries/add/', beneficiaries_views.BeneficiaryCreateView.as_view(), name='beneficiary_add'),
    path('beneficiaries/<uuid:pk>/', beneficiaries_views.BeneficiaryDetailView.as_view(), name='beneficiary_detail'),
    path('beneficiaries/<uuid:pk>/edit/', beneficiaries_views.BeneficiaryUpdateView.as_view(), name='beneficiary_edit'),
    path('beneficiaries/search/', beneficiaries_views.beneficiary_search, name='beneficiary_search'),
    path('beneficiaries/quick-add/', beneficiaries_views.beneficiary_quick_add, name='beneficiary_quick_add'),
    path('beneficiaries/<uuid:pk>/delete/', beneficiaries_views.beneficiary_delete, name='beneficiary_delete'),
    path('beneficiaries/export/excel/', beneficiaries_views.beneficiary_export_excel, name='beneficiary_export_excel'),
    path('beneficiaries/<uuid:pk>/export/excel/', beneficiaries_views.beneficiary_export_detail_excel, name='beneficiary_export_detail_excel'),
    path('beneficiaries/<uuid:pk>/export/pdf/', beneficiaries_views.beneficiary_export_detail_pdf, name='beneficiary_export_detail_pdf'),

    # Donors
    path('donors/', donors_views.DonorListView.as_view(), name='donor_list'),
    path('donors/add/', donors_views.DonorCreateView.as_view(), name='donor_add'),
    path('donors/<uuid:pk>/', donors_views.DonorDetailView.as_view(), name='donor_detail'),
    path('donors/<uuid:pk>/edit/', donors_views.DonorUpdateView.as_view(), name='donor_edit'),
    path('donors/<uuid:pk>/delete/', donors_views.donor_delete, name='donor_delete'),
    path('donors/export/excel/', donors_views.donor_export_excel, name='donor_export_excel'),

    # Donations
    path('donations/', donations_views.DonationListView.as_view(), name='donation_list'),
    path('donations/add/', donations_views.DonationCreateView.as_view(), name='donation_add'),
    path('donations/<uuid:pk>/', donations_views.DonationDetailView.as_view(), name='donation_detail'),
    path('donations/<uuid:pk>/receipt/', donations_views.donation_receipt, name='donation_receipt'),
    path('donations/export/excel/', donations_views.donation_export_excel, name='donation_export_excel'),

    # Sponsorships
    path('sponsorships/', sponsorships_views.SponsorshipListView.as_view(), name='sponsorship_list'),
    path('sponsorships/add/', sponsorships_views.SponsorshipCreateView.as_view(), name='sponsorship_add'),
    path('sponsorships/<uuid:pk>/', sponsorships_views.SponsorshipDetailView.as_view(), name='sponsorship_detail'),

    # Cases
    path('cases/', cases_views.CaseListView.as_view(), name='case_list'),
    path('cases/add/', cases_views.CaseCreateView.as_view(), name='case_add'),
    path('cases/<uuid:pk>/', cases_views.CaseDetailView.as_view(), name='case_detail'),
    path('cases/<uuid:pk>/approve/', cases_views.case_approve, name='case_approve'),
    path('cases/<uuid:pk>/reject/', cases_views.case_reject, name='case_reject'),
    path('cases/<uuid:pk>/disburse/', cases_views.case_disburse, name='case_disburse'),
    path('cases/<uuid:pk>/delete/', cases_views.case_delete, name='case_delete'),
    path('cases/<uuid:pk>/add-image/', cases_views.case_add_image, name='case_add_image'),
    path('cases/<uuid:pk>/delete-image/<uuid:image_id>/', cases_views.case_delete_image, name='case_delete_image'),
    path('cases/<uuid:pk>/add-feature/', cases_views.case_add_feature, name='case_add_feature'),
    path('cases/<uuid:pk>/delete-feature/<uuid:feature_id>/', cases_views.case_delete_feature, name='case_delete_feature'),
    path('cases/export/excel/', cases_views.case_export_excel, name='case_export_excel'),
    path('cases/type/<str:case_type>/', cases_views.case_type_view, name='case_type_view'),
    path('cases/type/<str:case_type>/export/', cases_views.case_type_export_excel, name='case_type_export'),

    # Projects
    path('projects/', projects_views.ProjectListView.as_view(), name='project_list'),
    path('projects/add/', projects_views.ProjectCreateView.as_view(), name='project_add'),
    path('projects/<uuid:pk>/', projects_views.ProjectDetailView.as_view(), name='project_detail'),
    path('projects/<uuid:pk>/edit/', projects_views.ProjectUpdateView.as_view(), name='project_edit'),

    # Finance
    path('finance/', finance_views.FinanceDashboardView.as_view(), name='finance_dashboard'),
    path('finance/entries/', finance_views.EntryListView.as_view(), name='entry_list'),
    path('finance/entries/add/', finance_views.EntryCreateView.as_view(), name='entry_add'),
    path('finance/entries/<uuid:pk>/', finance_views.EntryDetailView.as_view(), name='entry_detail'),
    path('finance/accounts/', finance_views.AccountListView.as_view(), name='account_list'),

    # Inventory
    path('inventory/', inventory_views.InventoryListView.as_view(), name='inventory_list'),
    path('inventory/items/add/', inventory_views.ItemCreateView.as_view(), name='item_add'),
    path('inventory/items/<uuid:pk>/', inventory_views.ItemDetailView.as_view(), name='item_detail'),
    path('inventory/transactions/add/', inventory_views.TransactionCreateView.as_view(), name='transaction_add'),

    # Employees
    path('employees/', employees_views.EmployeeListView.as_view(), name='employee_list'),
    path('employees/add/', employees_views.EmployeeCreateView.as_view(), name='employee_add'),
    path('employees/<uuid:pk>/', employees_views.EmployeeDetailView.as_view(), name='employee_detail'),

    # Occasions
    path('occasions/', include('apps.occasions.urls')),

    # Reports
    path('reports/', reports_views.reports_index, name='reports_index'),
    path('reports/beneficiaries/', reports_views.report_beneficiaries, name='report_beneficiaries'),
    path('reports/donations/', reports_views.report_donations, name='report_donations'),
    path('reports/finance/', reports_views.report_finance, name='report_finance'),
    path('reports/sponsorships/', reports_views.report_sponsorships, name='report_sponsorships'),
    path('reports/projects/', reports_views.report_projects, name='report_projects'),
    path('reports/inventory/', reports_views.report_inventory, name='report_inventory'),

    # API
    path('api/v1/', include('apps.accounts.api_urls')),
    path('api/v1/', include('apps.beneficiaries.api_urls')),
    path('api/v1/', include('apps.donors.api_urls')),
    path('api/v1/', include('apps.donations.api_urls')),
    path('api/v1/', include('apps.sponsorships.api_urls')),
    path('api/v1/', include('apps.cases.api_urls')),
    path('api/v1/', include('apps.projects.api_urls')),
    path('api/v1/', include('apps.finance.api_urls')),
    path('api/v1/', include('apps.inventory.api_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
