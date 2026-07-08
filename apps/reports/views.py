from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.db.models import F
from django.utils import timezone
from datetime import timedelta
from apps.beneficiaries.models import Beneficiary
from apps.donors.models import Donor
from apps.donations.models import Donation
from apps.sponsorships.models import Sponsorship
from apps.projects.models import Project
from apps.finance.models import FinancialEntry, Account
from apps.cases.models import Case
from apps.inventory.models import InventoryItem, InventoryTransaction


@login_required
def reports_index(request):
    return render(request, 'reports/index.html')


@login_required
def report_beneficiaries(request):
    qs = Beneficiary.objects.select_related('branch').filter(is_active=True)
    from_date = request.GET.get('from', '')
    to_date = request.GET.get('to', '')
    if from_date:
        qs = qs.filter(created_at__gte=from_date)
    if to_date:
        qs = qs.filter(created_at__lte=to_date)
    total = qs.count()
    active = qs.filter(is_active=True).count()
    orphans = qs.filter(has_orphans=True).count()
    urgent = qs.filter(priority_score__gte=70).count()
    return render(request, 'reports/beneficiaries.html', {
        'total': total, 'active': active, 'orphans': orphans,
        'urgent': urgent, 'beneficiaries': qs.order_by('-priority_score')[:100],
        'from_date': from_date, 'to_date': to_date,
    })


@login_required
def report_donations(request):
    qs = Donation.objects.select_related('donor', 'project', 'received_by').filter(status='confirmed')
    donation_type = request.GET.get('donation_type', '')
    from_date = request.GET.get('from', '')
    to_date = request.GET.get('to', '')
    if donation_type:
        qs = qs.filter(donation_type=donation_type)
    if from_date:
        qs = qs.filter(receipt_date__gte=from_date)
    if to_date:
        qs = qs.filter(receipt_date__lte=to_date)
    total_amount = qs.aggregate(total=Sum('amount'))['total'] or 0
    count = qs.count()
    cash_total = qs.filter(payment_method='cash').aggregate(total=Sum('amount'))['total'] or 0
    bank_total = qs.filter(payment_method='transfer').aggregate(total=Sum('amount'))['total'] or 0
    return render(request, 'reports/donations.html', {
        'total_amount': total_amount, 'count': count,
        'cash_total': cash_total, 'bank_total': bank_total,
        'donations': qs.order_by('-receipt_date')[:100],
        'donation_type': donation_type, 'from_date': from_date, 'to_date': to_date,
    })


@login_required
def report_finance(request):
    qs = FinancialEntry.objects.select_related('account', 'recorded_by', 'donor').filter(is_approved=True)
    from_date = request.GET.get('from', '')
    to_date = request.GET.get('to', '')
    if from_date:
        qs = qs.filter(entry_date__gte=from_date)
    if to_date:
        qs = qs.filter(entry_date__lte=to_date)
    total_income = qs.filter(entry_type='income').aggregate(total=Sum('amount'))['total'] or 0
    total_expense = qs.filter(entry_type='expense').aggregate(total=Sum('amount'))['total'] or 0
    entries = qs.order_by('-entry_date')[:100]
    return render(request, 'reports/finance.html', {
        'total_income': total_income, 'total_expense': total_expense,
        'balance': total_income - total_expense,
        'entries': entries, 'from_date': from_date, 'to_date': to_date,
    })


@login_required
def report_sponsorships(request):
    active = Sponsorship.objects.filter(is_active=True).count()
    total_monthly = Sponsorship.objects.filter(is_active=True).aggregate(total=Sum('monthly_amount'))['total'] or 0
    by_type = Sponsorship.objects.values('sponsorship_type').annotate(count=Count('id'))
    by_status = Sponsorship.objects.values('status').annotate(count=Count('id'))
    sponsorships = Sponsorship.objects.select_related('beneficiary', 'sponsor').all()[:100]
    return render(request, 'reports/sponsorships.html', {
        'active': active, 'total_monthly': total_monthly,
        'by_type': by_type, 'by_status': by_status,
        'sponsorships': sponsorships,
    })


@login_required
def report_projects(request):
    total = Project.objects.count()
    active_count = Project.objects.filter(status='in_progress').count()
    completed = Project.objects.filter(status='completed').count()
    by_type = Project.objects.values('project_type').annotate(count=Count('id'))
    by_status = Project.objects.values('status').annotate(count=Count('id'))
    total_budget = Project.objects.aggregate(total=Sum('total_budget'))['total'] or 0
    total_spent = Project.objects.aggregate(total=Sum('total_spent'))['total'] or 0
    projects = Project.objects.select_related('manager').all()[:100]
    return render(request, 'reports/projects.html', {
        'total': total, 'active_count': active_count, 'completed': completed,
        'by_type': by_type, 'by_status': by_status,
        'total_budget': total_budget, 'total_spent': total_spent,
        'projects': projects,
    })


@login_required
def report_inventory(request):
    total_items = InventoryItem.objects.filter(is_active=True).count()
    total_quantity = InventoryItem.objects.filter(is_active=True).aggregate(total=Sum('quantity'))['total'] or 0
    low_stock = InventoryItem.objects.filter(is_active=True, quantity__lte=F('min_quantity')).count()
    by_category = InventoryItem.objects.filter(is_active=True).values('category__name').annotate(
        count=Count('id'), total_qty=Sum('quantity')).order_by('category__name')
    recent_transactions = InventoryTransaction.objects.select_related('item__category').order_by('-created_at')[:20]
    items = InventoryItem.objects.select_related('category').filter(is_active=True).order_by('name')[:100]
    return render(request, 'reports/inventory.html', {
        'total_items': total_items, 'total_quantity': total_quantity,
        'low_stock': low_stock, 'by_category': by_category,
        'recent_transactions': recent_transactions, 'items': items,
    })
