from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q, F
from .models import InventoryItem, InventoryCategory, InventoryTransaction


class InventoryListView(LoginRequiredMixin, ListView):
    model = InventoryItem
    template_name = 'inventory/list.html'
    context_object_name = 'items'
    paginate_by = 25

    def get_queryset(self):
        qs = InventoryItem.objects.select_related('category').filter(is_active=True)
        search = self.request.GET.get('search')
        if search:
            qs = qs.filter(Q(code__icontains=search) | Q(name__icontains=search))
        category = self.request.GET.get('category')
        if category:
            qs = qs.filter(category_id=category)
        low_stock = self.request.GET.get('low_stock')
        if low_stock:
            qs = qs.filter(quantity__lte=F('min_quantity'))
        return qs.order_by('name')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = InventoryCategory.objects.all()
        ctx.update({k: self.request.GET.get(k, '') for k in ['search', 'category', 'low_stock']})
        return ctx


class ItemCreateView(LoginRequiredMixin, CreateView):
    model = InventoryItem
    template_name = 'inventory/item_form.html'
    fields = ['name', 'category', 'unit', 'quantity', 'min_quantity', 'max_quantity',
              'unit_price', 'expiry_date', 'location', 'notes']
    success_url = '/inventory/'

    def form_valid(self, form):
        messages.success(self.request, 'تم إضافة الصنف')
        return super().form_valid(form)


class ItemDetailView(LoginRequiredMixin, DetailView):
    model = InventoryItem
    template_name = 'inventory/item_detail.html'
    context_object_name = 'item'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['transactions'] = InventoryTransaction.objects.filter(item=self.object).order_by('-created_at')[:30]
        return ctx


class TransactionCreateView(LoginRequiredMixin, CreateView):
    model = InventoryTransaction
    template_name = 'inventory/transaction_form.html'
    fields = ['item', 'transaction_type', 'quantity', 'unit_price', 'source',
              'beneficiary', 'case', 'project', 'notes']

    def form_valid(self, form):
        form.instance.performed_by = self.request.user
        messages.success(self.request, 'تم تسجيل الحركة المخزنية')
        return super().form_valid(form)

    def get_success_url(self):
        return f'/inventory/items/{self.object.item.id}/'
