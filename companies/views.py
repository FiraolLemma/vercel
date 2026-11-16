from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from users.roles import UserRole, role_required

from .forms import CompanyForm, FarmForm
from .models import Company, Farm


ORGANIZATION_ROLES = (
    UserRole.FARMER,
    UserRole.SUPPLIER,
    UserRole.VETERINARIAN,
    UserRole.SERVICE_PROVIDER,
)


def _owned_or_staff(queryset, user):
    return (
        queryset
        if user.is_staff and not user.is_virtual_user
        else queryset.filter(owner=user)
    )


@login_required
def manage_organizations(request):
    companies = _owned_or_staff(
        Company.objects.all().select_related("owner"),
        request.user,
    )
    farms = _owned_or_staff(
        Farm.objects.all().select_related("owner", "company"),
        request.user,
    )
    return render(
        request,
        "companies/manage.html",
        {
            "companies": companies,
            "farms": farms,
            "can_manage_organizations": request.user.is_staff
            or any(request.user.has_role(role) for role in ORGANIZATION_ROLES),
        },
    )


@role_required(*ORGANIZATION_ROLES)
def company_create(request):
    form = CompanyForm(request.POST or None, user=request.user)
    if request.method == "POST" and form.is_valid():
        company = form.save(commit=False)
        company.owner = request.user
        company.save()
        messages.success(request, "Company created.")
        return redirect("companies:company_detail", pk=company.pk)
    return render(
        request,
        "companies/form.html",
        {"form": form, "form_title": "Create company"},
    )


@login_required
def company_detail(request, pk):
    company = get_object_or_404(
        _owned_or_staff(Company.objects.select_related("owner"), request.user),
        pk=pk,
    )
    return render(
        request,
        "companies/detail.html",
        {"organization": company, "is_farm": False},
    )


@role_required(*ORGANIZATION_ROLES)
def company_update(request, pk):
    company = get_object_or_404(
        _owned_or_staff(Company.objects.all(), request.user),
        pk=pk,
    )
    form = CompanyForm(request.POST or None, instance=company, user=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Company updated.")
        return redirect("companies:company_detail", pk=company.pk)
    return render(
        request,
        "companies/form.html",
        {"form": form, "form_title": "Update company"},
    )


@role_required(*ORGANIZATION_ROLES)
@require_POST
def company_delete(request, pk):
    company = get_object_or_404(
        _owned_or_staff(Company.objects.all(), request.user),
        pk=pk,
    )
    company.delete()
    messages.success(request, "Company removed.")
    return redirect("companies:manage")


@role_required(*ORGANIZATION_ROLES)
def farm_create(request):
    form = FarmForm(request.POST or None, user=request.user)
    if request.method == "POST" and form.is_valid():
        farm = form.save(commit=False)
        farm.owner = request.user
        farm.save()
        messages.success(request, "Farm created.")
        return redirect("companies:farm_detail", pk=farm.pk)
    return render(
        request,
        "companies/form.html",
        {"form": form, "form_title": "Create farm"},
    )


@login_required
def farm_detail(request, pk):
    farm = get_object_or_404(
        _owned_or_staff(Farm.objects.select_related("owner", "company"), request.user),
        pk=pk,
    )
    return render(
        request,
        "companies/detail.html",
        {"organization": farm, "is_farm": True},
    )


@role_required(*ORGANIZATION_ROLES)
def farm_update(request, pk):
    farm = get_object_or_404(
        _owned_or_staff(Farm.objects.all(), request.user),
        pk=pk,
    )
    form = FarmForm(request.POST or None, instance=farm, user=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Farm updated.")
        return redirect("companies:farm_detail", pk=farm.pk)
    return render(
        request,
        "companies/form.html",
        {"form": form, "form_title": "Update farm"},
    )


@role_required(*ORGANIZATION_ROLES)
@require_POST
def farm_delete(request, pk):
    farm = get_object_or_404(
        _owned_or_staff(Farm.objects.all(), request.user),
        pk=pk,
    )
    farm.delete()
    messages.success(request, "Farm removed.")
    return redirect("companies:manage")

def companies_view(request):
    """
    View for companies index page
    """
    context = {
        'title': 'Companies',
        'description': 'List of companies',
        # Add any other context data needed for the template
    }
    return render(request, 'companies/index.html', context)

def alema_view(request):
    """
    View for AlemA company page
    """
    context = {
        'title': 'AlemA Poultry',
        'description': 'Information about AlemA Poultry company',
        # Add any other context data needed for the template
    }
    return render(request, 'companies/alema.html', context)

def ethiochicken_view(request):
    """
    View for EthioChicken company page
    """
    context = {
        'title': 'EthioChicken',
        'description': 'Information about EthioChicken company',
        # Add any other context data needed for the template
    }
    return render(request, 'companies/ethiochicken.html', context)

def nvi_view(request):
    """
    View for NVI company page
    """
    context = {
        'title': 'NVI',
        'description': 'Information about NVI company',
        # Add any other context data needed for the template
    }
    return render(request, 'companies/nvi.html', context)