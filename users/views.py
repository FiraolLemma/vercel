# users/views.py
from django.contrib.auth import login, logout as auth_logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from conversation.models import ConversationMessage

from .forms import (
    PhoneLoginForm,
    PinChangeForm,
    ProfileCreateForm,
    ProfileUpdateForm,
    UserRegisterForm,
)
from .models import CustomUser
from .roles import UserRole

@login_required
def unread_count_api(request):
    """API endpoint to get unread message count"""
    total_unread = ConversationMessage.objects.filter(
        conversation__members=request.user,
        is_read=False,
    ).exclude(created_by=request.user).count()
    return JsonResponse({'total_unread': total_unread})

@require_POST
def user_logout(request):
    auth_logout(request)
    return redirect('base:index')

@login_required
def dashboard(request):
    """Dashboard view after successful login"""
    return render(request, 'users/dashboard.html')

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)

        if form.is_valid():
            try:
                user = form.save()

                login(
                    request,
                    user,
                    backend=settings.AUTHENTICATION_BACKENDS[0]
                )

                return redirect('users:profile_create')

            except Exception:
                import logging
                logging.exception(
                    "Registration failed during user creation or login"
                )
                raise

    else:
        form = UserRegisterForm()

    return render(
        request,
        'users/register.html',
        {'form': form}
    )

def user_login(request):
    form = PhoneLoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        next_url = request.POST.get('next') or request.GET.get('next')
        if next_url and url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            return redirect(next_url)
        return redirect(settings.LOGIN_REDIRECT_URL)
    return render(
        request,
        'users/login.html',
        {'form': form, 'next': request.POST.get('next') or request.GET.get('next', '')},
    )

@login_required
def profile_create(request):
    if request.user.onboarding_complete:
        return redirect("users:profile_update")

    if request.method == 'POST':
        form = ProfileCreateForm(
            request.POST,
            request.FILES,
            instance=request.user,
        )
        if form.is_valid():
            form.save()
            return redirect("users:dashboard")
    else:
        form = ProfileCreateForm(instance=request.user)

    return render(request, 'users/profile_create.html', {'form': form})

@login_required
def profile_update(request):
    if not request.user.onboarding_complete:
        return redirect('users:profile_create')
        
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('users:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'users/profile_update.html', {'form': form})

@login_required
def profile(request):
    return render(
        request,
        'users/profile.html',
        {
            'user': request.user,
            'companies': request.user.companies.all(),
            'farms': request.user.farms.select_related('company').all(),
            'can_manage_organizations': request.user.is_staff
            or any(
                request.user.has_role(role)
                for role in (
                    UserRole.FARMER,
                    UserRole.SUPPLIER,
                    UserRole.VETERINARIAN,
                    UserRole.SERVICE_PROVIDER,
                )
            ),
        },
    )

def seller_profile(request, user_id):
    """View for displaying another user's profile"""
    User = get_user_model()
    seller = get_object_or_404(User, id=user_id)
    return render(request, 'users/seller_profile.html', {'seller': seller})

@login_required
@user_passes_test(lambda user: user.is_staff, login_url='users:login')
def user_list(request):
    """View for listing all users"""
    users = CustomUser.objects.all().prefetch_related('groups')
    return render(request, 'users/users.html', {'users': users})


@login_required
def pin_change(request):
    form = PinChangeForm(request.POST or None, user=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        update_session_auth_hash(request, request.user)
        return redirect("users:password_change_done")
    return render(request, "users/password_change.html", {"form": form})