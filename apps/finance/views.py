from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.contrib import messages
from django.db.models import Q, Sum
from django.db import models
from .models import FinancialEntry, Account, BankAccount


class FinanceDashboardView(LoginRequiredMixin, ListView):
    template_name = 'finance/dashboard.html'

    def get(self, request, *args, **kwargs):
        total_income = FinancialEntry.objects.filter(entry_type='income', is_approved=True).aggregate(
            total=Sum('amount'))['total'] or 0
        total_expense = FinancialEntry.objects.filter(entry_type='expense', is_approved=True).aggregate(
            total=Sum('amount'))['total'] or 0
        pending_entries = FinancialEntry.objects.filter(is_approved=False).count()
        bank_total = BankAccount.objects.filter(is_active=True).aggregate(
            total=Sum('current_balance'))['total'] or 0
        accounts = Account.objects.filter(is_active=True).order_by('code')
        recent_entries = FinancialEntry.objects.select_related('account').order_by('-created_at')[:20]
        zakat_total = FinancialEntry.objects.filter(transaction_type='zakat', is_approved=True).aggregate(
            total=Sum('amount'))['total'] or 0

        # Income vs Expense by month
        month_data = []
        from django.utils import timezone
        today = timezone.now()
        for i in range(6):
            m = today.month - i
            y = today.year
            if m <= 0:
                m += 12
                y -= 1
            inc = FinancialEntry.objects.filter(entry_type='income', is_approved=True,
                entry_date__year=y, entry_date__month=m).aggregate(t=Sum('amount'))['t'] or 0
            exp = FinancialEntry.objects.filter(entry_type='expense', is_approved=True,
                entry_date__year=y, entry_date__month=m).aggregate(t=Sum('amount'))['t'] or 0
            month_data.insert(0, {'month': f'{m:02d}/{y}', 'income': float(inc), 'expense': float(exp)})

        return render(request, self.template_name, {
            'total_income': total_income,
            'total_expense': total_expense,
            'balance': total_income - total_expense,
            'pending_entries': pending_entries,
            'bank_total': bank_total,
            'accounts': accounts,
            'recent_entries': recent_entries,
            'zakat_total': zakat_total,
            'month_data': month_data,
        })


class EntryListView(LoginRequiredMixin, ListView):
    model = FinancialEntry
    template_name = 'finance/entries.html'
    context_object_name = 'entries'
    paginate_by = 25

    def get_queryset(self):
        qs = FinancialEntry.objects.select_related('account', 'recorded_by').all()
        entry_type = self.request.GET.get('entry_type')
        if entry_type:
            qs = qs.filter(entry_type=entry_type)
        txn_type = self.request.GET.get('transaction_type')
        if txn_type:
            qs = qs.filter(transaction_type=txn_type)
        date_from = self.request.GET.get('date_from')
        if date_from:
            qs = qs.filter(entry_date__gte=date_from)
        date_to = self.request.GET.get('date_to')
        if date_to:
            qs = qs.filter(entry_date__lte=date_to)
        approved = self.request.GET.get('approved')
        if approved:
            qs = qs.filter(is_approved=(approved == '1'))
        return qs.order_by('-entry_date', '-created_at')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({k: self.request.GET.get(k, '') for k in ['entry_type', 'transaction_type', 'date_from', 'date_to', 'approved']})
        qs = self.get_queryset()
        ctx['total_amount'] = qs.aggregate(total=Sum('amount'))['total'] or 0
        return ctx


class EntryCreateView(LoginRequiredMixin, CreateView):
    model = FinancialEntry
    template_name = 'finance/entry_form.html'
    fields = ['entry_type', 'entry_date', 'amount', 'description', 'account',
              'payment_method', 'transaction_type', 'reference_number', 'notes']
    success_url = '/finance/entries/'

    def form_valid(self, form):
        form.instance.recorded_by = self.request.user
        if form.instance.entry_type == 'expense':
            form.instance.is_approved = False
        else:
            form.instance.is_approved = True
        messages.success(self.request, 'تم تسجيل القيد المالي')
        return super().form_valid(form)


class EntryDetailView(LoginRequiredMixin, DetailView):
    model = FinancialEntry
    template_name = 'finance/entry_detail.html'
    context_object_name = 'entry'


class AccountListView(LoginRequiredMixin, ListView):
    model = Account
    template_name = 'finance/accounts.html'
    context_object_name = 'accounts'

    def get_queryset(self):
        return Account.objects.filter(is_active=True).order_by('code')
