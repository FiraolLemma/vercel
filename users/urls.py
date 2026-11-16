# users/urls.py
from django.contrib.auth import views as auth_views
from django.urls import path

from .views import user_login, dashboard
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', user_login, name='login'),
    path('dashboard/', dashboard, name='dashboard'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.profile_update, name='profile_update'),
    path('api/unread-count/', views.unread_count_api, name='unread_count_api'),
    path('seller_profile/<int:user_id>/', views.seller_profile, name='seller_profile'),
    path('users/', views.user_list, name='user_list'),
    path('profile/create/', views.profile_create, name='profile_create'),
    path(
        'password/change/',
        views.pin_change,
        name='password_change',
    ),
    path(
        'password/change/done/',
        auth_views.PasswordChangeDoneView.as_view(
            template_name='users/password_change_done.html',
        ),
        name='password_change_done',
    ),
]