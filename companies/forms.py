from django import forms

from .models import Company, Farm


class OrganizationSelectionMixin:
    company = forms.ModelChoiceField(
        queryset=Company.objects.none(),
        required=False,
        empty_label="No company selected",
    )
    farm = forms.ModelChoiceField(
        queryset=Farm.objects.none(),
        required=False,
        empty_label="No farm selected",
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None and user.is_staff:
            self.fields["company"].queryset = Company.objects.all()
            self.fields["farm"].queryset = Farm.objects.select_related("company").all()
        elif user is not None and user.is_authenticated:
            self.fields["company"].queryset = Company.objects.filter(owner=user)
            self.fields["farm"].queryset = Farm.objects.filter(owner=user).select_related(
                "company"
            )

    def clean(self):
        cleaned_data = super().clean()
        farm = cleaned_data.get("farm")
        company = cleaned_data.get("company")
        if farm and farm.company_id:
            if company and company.pk != farm.company_id:
                self.add_error("company", "Choose the company associated with this farm.")
            elif not company:
                cleaned_data["company"] = farm.company
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.company = self.cleaned_data.get("company")
        instance.farm = self.cleaned_data.get("farm")
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ("name", "description", "email", "phone", "website", "location")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if self.user is not None and Company.objects.filter(
            owner=self.user,
            name__iexact=name,
        ).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("You already have a company with this name.")
        return name


class FarmForm(forms.ModelForm):
    class Meta:
        model = Farm
        fields = (
            "company",
            "name",
            "description",
            "city",
            "region",
            "country",
            "address",
            "phone",
            "email",
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "address": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        if user is not None and user.is_staff:
            self.fields["company"].queryset = Company.objects.all()
        elif user is not None and user.is_authenticated:
            self.fields["company"].queryset = Company.objects.filter(owner=user)
        else:
            self.fields["company"].queryset = Company.objects.none()

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if self.user is not None and Farm.objects.filter(
            owner=self.user,
            name__iexact=name,
        ).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("You already have a farm with this name.")
        return name
