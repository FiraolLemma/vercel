from django.urls import path
from . import views

app_name = 'companies'

urlpatterns = [
    path('manage/', views.manage_organizations, name='manage'),
    path('manage/companies/create/', views.company_create, name='company_create'),
    path('manage/companies/<int:pk>/', views.company_detail, name='company_detail'),
    path('manage/companies/<int:pk>/edit/', views.company_update, name='company_update'),
    path('manage/companies/<int:pk>/delete/', views.company_delete, name='company_delete'),
    path('manage/farms/create/', views.farm_create, name='farm_create'),
    path('manage/farms/<int:pk>/', views.farm_detail, name='farm_detail'),
    path('manage/farms/<int:pk>/edit/', views.farm_update, name='farm_update'),
    path('manage/farms/<int:pk>/delete/', views.farm_delete, name='farm_delete'),
    path('', views.companies_view, name='index'),
    path('alema/', views.alema_view, name='alema'),
    path('ethiochicken/', views.ethiochicken_view, name='ethiochicken'),
    path('nvi/', views.nvi_view, name='nvi'),
]