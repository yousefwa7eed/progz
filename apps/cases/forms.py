from django import forms
from .models import Case, CaseFeature


class CaseForm(forms.ModelForm):
    class Meta:
        model = Case
        fields = ['beneficiary', 'case_type', 'priority', 'description',
                  'requested_amount', 'assigned_to', 'notes']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'requested_amount': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['beneficiary'].widget.attrs.update({'class': 'form-select select2', 'required': True})
        self.fields['case_type'].widget.attrs.update({'class': 'form-select', 'required': True})
        self.fields['priority'].widget.attrs.update({'class': 'form-select', 'required': True})
        self.fields['assigned_to'].widget.attrs.update({'class': 'form-select'})
        self.fields['assigned_to'].required = False
        self.fields['requested_amount'].required = False
        self.fields['notes'].required = False
