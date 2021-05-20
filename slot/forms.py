from django import forms

from slot.models import Haulier


class SlotHaulierForm(forms.ModelForm):
    class Meta:
        model = Haulier
        fields = ['code', 'name', 'contact', 'telephone', 'email', 'is_use', ]

    def clean_code(self):
        code = self.cleaned_data.get("code")
        queryset = Haulier.objects.filter(code__exact=code, position=self.initial['position'])
        if queryset:
            raise forms.ValidationError('Code already exist. Please Change it.')
        return code.upper()


class SlotHaulierUpdateForm(forms.ModelForm):
    class Meta:
        model = Haulier
        fields = ['name', 'contact', 'telephone', 'email', 'is_use', ]

