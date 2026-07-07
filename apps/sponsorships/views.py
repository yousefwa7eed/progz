from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from .models import Sponsorship, SponsorshipPayment
from apps.finance.models import FinancialEntry, Account


class SponsorshipListView(LoginRequiredMixin, ListView):
    model = Sponsorship
    template_name = 'sponsorships/list.html'
    context_object_name = 'sponsorships'
    paginate_by = 25

    def get_queryset(self):
        qs = Sponsorship.objects.select_related('sponsor', 'beneficiary').all()
        search = self.request.GET.get('search')
        if search:
            qs = qs.filter(Q(code__icontains=search) | Q(sponsor__full_name__icontains=search) |
                           Q(beneficiary__full_name__icontains=search))
        s_type = self.request.GET.get('type')
        if s_type:
            qs = qs.filter(sponsorship_type=s_type)
        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)
        return qs.order_by('-created_at')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search'] = self.request.GET.get('search', '')
        ctx['type_filter'] = self.request.GET.get('type', '')
        ctx['status_filter'] = self.request.GET.get('status', '')
        return ctx


class SponsorshipCreateView(LoginRequiredMixin, CreateView):
    model = Sponsorship
    template_name = 'sponsorships/form.html'
    fields = ['sponsor', 'beneficiary', 'sponsorship_type', 'monthly_amount',
              'start_date', 'duration_months', 'is_permanent', 'payment_method',
              'payment_day', 'notes']
    success_url = '/sponsorships/'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        if form.instance.duration_months and not form.instance.is_permanent:
            from datetime import date
            from dateutil.relativedelta import relativedelta
            form.instance.end_date = form.instance.start_date + relativedelta(months=form.instance.duration_months)
        messages.success(self.request, 'تم إنشاء الكفالة بنجاح')
        return super().form_valid(form)


class SponsorshipDetailView(LoginRequiredMixin, DetailView):
    model = Sponsorship
    template_name = 'sponsorships/detail.html'
    context_object_name = 'sponsorship'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['payments'] = SponsorshipPayment.objects.filter(sponsorship=self.object).order_by('-payment_date')
        return ctx
