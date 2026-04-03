from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('staff', 'Staff'),
        ('student', 'Student'),
        ('visitor', 'Visitor'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    matric_or_staff_id = models.CharField(max_length=50, blank=True)
    department = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name()} [{self.get_role_display()}]"

    def is_admin(self):
        return self.role == 'admin'


class Vehicle(models.Model):
    VEHICLE_TYPE_CHOICES = [
        ('car', 'Car'),
        ('motorcycle', 'Motorcycle'),
        ('bus', 'Bus / Minivan'),
        ('truck', 'Truck'),
        ('other', 'Other'),
    ]
    CATEGORY_CHOICES = [
        ('student', 'Student'),
        ('staff', 'Academic Staff'),
        ('non_academic', 'Non-Academic Staff'),
        ('visitor', 'Visitor'),
        ('official', 'Official'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
    ]

    plate_number = models.CharField(max_length=20, unique=True)
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPE_CHOICES)
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=30)
    year = models.PositiveIntegerField(null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vehicles')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    registered_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.plate_number} — {self.make} {self.model}"

    class Meta:
        ordering = ['-registered_at']


class IncidentReport(models.Model):
    INCIDENT_TYPE_CHOICES = [
        ('congestion', 'Congestion'),
        ('parking', 'Illegal Parking'),
        ('near_miss', 'Near-miss / Accident'),
        ('violation', 'Traffic Violation'),
        ('obstruction', 'Road Obstruction'),
        ('other', 'Other'),
    ]
    LOCATION_CHOICES = [
        ('main_gate', 'Main Gate'),
        ('admin_block', 'Admin Block Road'),
        ('library', 'Library Parking'),
        ('science_block', 'Science Block'),
        ('hostel_road', 'Hostel Road'),
        ('staff_quarters', 'Staff Quarters'),
        ('other', 'Other'),
    ]
    PRIORITY_CHOICES = [
        ('normal', 'Normal'),
        ('high', 'High'),
        ('emergency', 'Emergency'),
    ]
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('pending', 'Pending'),
        ('resolved', 'Resolved'),
    ]

    incident_type = models.CharField(max_length=30, choices=INCIDENT_TYPE_CHOICES)
    location = models.CharField(max_length=30, choices=LOCATION_CHOICES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal')
    description = models.TextField()
    vehicle_plate = models.CharField(max_length=20, blank=True)
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='incidents')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    reported_at = models.DateTimeField(default=timezone.now)
    resolved_at = models.DateTimeField(null=True, blank=True)
    admin_note = models.TextField(blank=True)

    def __str__(self):
        return f"#{self.pk} {self.get_incident_type_display()} at {self.get_location_display()}"

    class Meta:
        ordering = ['-reported_at']


class AdminAction(models.Model):
    ACTION_CHOICES = [
        ('vehicle_approved', 'Vehicle Approved'),
        ('vehicle_suspended', 'Vehicle Suspended'),
        ('incident_resolved', 'Incident Resolved'),
        ('user_suspended', 'User Suspended'),
        ('user_activated', 'User Activated'),
        ('other', 'Other'),
    ]
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_actions')
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    description = models.TextField()
    performed_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.get_action_display()} by {self.admin.username}"

    class Meta:
        ordering = ['-performed_at']
