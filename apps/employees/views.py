from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.contrib import messages
from django.db.models import Q
from .models import Employee, Attendance, Task


class EmployeeListView(LoginRequiredMixin, ListView):
    model = Employee
    template_name = 'employees/list.html'
    context_object_name = 'employees'
    paginate_by = 25

    def get_queryset(self):
        qs = Employee.objects.select_related('branch').all()
        search = self.request.GET.get('search')
        if search:
            qs = qs.filter(Q(full_name__icontains=search) | Q(employee_code__icontains=search) | Q(phone__icontains=search))
        etype = self.request.GET.get('employee_type')
        if etype:
            qs = qs.filter(employee_type=etype)
        dept = self.request.GET.get('department')
        if dept:
            qs = qs.filter(department__icontains=dept)
        return qs.order_by('full_name')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['departments'] = Employee.objects.values_list('department', flat=True).distinct()
        ctx.update({k: self.request.GET.get(k, '') for k in ['search', 'employee_type', 'department']})
        return ctx


class EmployeeCreateView(LoginRequiredMixin, CreateView):
    model = Employee
    template_name = 'employees/form.html'
    fields = ['full_name', 'employee_type', 'position', 'department', 'phone',
              'email', 'hire_date', 'contract_type', 'salary', 'qualifications', 'skills', 'notes']
    success_url = '/employees/'


class EmployeeDetailView(LoginRequiredMixin, DetailView):
    model = Employee
    template_name = 'employees/detail.html'
    context_object_name = 'employee'
