from django import forms
from .models import Occasion, OccasionMember, OccasionTask


class OccasionForm(forms.ModelForm):
    class Meta:
        model = Occasion
        fields = ['name', 'description', 'support_type', 'custom_support_type', 'budget_enabled', 'budget_amount', 'start_date', 'end_date', 'is_recurring', 'status']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'support_type': forms.Select(attrs={'class': 'form-select'}),
            'custom_support_type': forms.TextInput(attrs={'class': 'form-control'}),
            'budget_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'budget_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_recurring': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    class Media:
        js = ('js/occasion_form.js',)


class MemberAddForm(forms.ModelForm):
    class Meta:
        model = OccasionMember
        fields = ['member_type', 'case', 'beneficiary', 'notes']
        widgets = {
            'member_type': forms.Select(attrs={'class': 'form-select', 'id': 'id_member_type'}),
            'case': forms.Select(attrs={'class': 'form-select select2-case', 'id': 'id_case'}),
            'beneficiary': forms.Select(attrs={'class': 'form-select select2-beneficiary', 'id': 'id_beneficiary'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class TaskForm(forms.ModelForm):
    class Meta:
        model = OccasionTask
        fields = ['task_name', 'status', 'notes']
        widgets = {
            'task_name': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class BulkMemberAddForm(forms.Form):
    member_type = forms.ChoiceField(
        choices=[('case', 'حالة'), ('beneficiary', 'مستفيد')],
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_bulk_member_type'}),
        label='النوع',
    )
    case_ids = forms.MultipleChoiceField(
        choices=[],
        widget=forms.SelectMultiple(attrs={'class': 'form-select select2-multi', 'id': 'id_case_ids'}),
        required=False,
        label='الحالات',
    )
    beneficiary_ids = forms.MultipleChoiceField(
        choices=[],
        widget=forms.SelectMultiple(attrs={'class': 'form-select select2-multi', 'id': 'id_beneficiary_ids'}),
        required=False,
        label='المستفيدين',
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        required=False,
        label='ملاحظات عامة',
    )
