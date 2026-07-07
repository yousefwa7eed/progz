from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Project, ProjectPhase


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'projects/list.html'
    context_object_name = 'projects'
    paginate_by = 25

    def get_queryset(self):
        qs = Project.objects.select_related('manager').all()
        search = self.request.GET.get('search')
        if search:
            qs = qs.filter(Q(code__icontains=search) | Q(name__icontains=search))
        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)
        ptype = self.request.GET.get('project_type')
        if ptype:
            qs = qs.filter(project_type=ptype)
        return qs.order_by('-created_at')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({k: self.request.GET.get(k, '') for k in ['search', 'status', 'project_type']})
        return ctx


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    template_name = 'projects/form.html'
    fields = ['name', 'project_type', 'description', 'goal_amount', 'total_budget',
              'start_date', 'end_date', 'manager', 'beneficiaries_count', 'locations', 'notes']
    success_url = '/projects/'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'تم إنشاء المشروع بنجاح')
        return super().form_valid(form)


class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'projects/detail.html'
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['phases'] = ProjectPhase.objects.filter(project=self.object).order_by('start_date')
        return ctx


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    template_name = 'projects/form.html'
    fields = ['name', 'project_type', 'description', 'goal_amount', 'total_budget',
              'start_date', 'end_date', 'status', 'manager', 'beneficiaries_count', 'locations', 'notes']
    success_url = '/projects/'

    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث المشروع')
        return super().form_valid(form)
