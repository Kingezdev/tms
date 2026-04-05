from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Vehicles
    path('vehicles/', views.vehicle_list, name='vehicle_list'),
    path('vehicles/register/', views.vehicle_register, name='vehicle_register'),
    path('vehicles/<int:pk>/', views.vehicle_detail, name='vehicle_detail'),
    path('vehicles/<int:pk>/edit/', views.vehicle_edit, name='vehicle_edit'),

    # Incidents
    path('incidents/', views.incident_list, name='incident_list'),
    path('incidents/report/', views.incident_report, name='incident_report'),
    path('incidents/<int:pk>/', views.incident_detail, name='incident_detail'),

    # Admin only
    path('users/', views.user_list, name='user_list'),
    path('users/<int:pk>/', views.user_detail, name='user_detail'),
    path('reports/', views.reports_view, name='reports'),
]
