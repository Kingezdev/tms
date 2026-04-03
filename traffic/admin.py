from django.contrib import admin
from .models import UserProfile, Vehicle, IncidentReport, AdminAction


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'department', 'matric_or_staff_id', 'phone']
    list_filter = ['role']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'matric_or_staff_id']


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['plate_number', 'make', 'model', 'color', 'owner', 'category', 'status', 'registered_at']
    list_filter = ['status', 'category', 'vehicle_type']
    search_fields = ['plate_number', 'make', 'model', 'owner__username']
    list_editable = ['status']


@admin.register(IncidentReport)
class IncidentReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'incident_type', 'location', 'priority', 'reported_by', 'status', 'reported_at']
    list_filter = ['status', 'incident_type', 'priority', 'location']
    search_fields = ['description', 'vehicle_plate', 'reported_by__username']
    list_editable = ['status']


@admin.register(AdminAction)
class AdminActionAdmin(admin.ModelAdmin):
    list_display = ['action', 'admin', 'description', 'performed_at']
    list_filter = ['action']
    search_fields = ['description', 'admin__username']
