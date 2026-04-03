from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import UserProfile, Vehicle, IncidentReport, AdminAction
from .forms import (RegisterForm, VehicleForm, IncidentReportForm,
                    ResolveIncidentForm, VehicleStatusForm, UserProfileForm)


# ─── Helper decorator ────────────────────────────────────────
def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        try:
            if not request.user.profile.is_admin():
                messages.error(request, 'Access denied. Administrators only.')
                return redirect('dashboard')
        except UserProfile.DoesNotExist:
            messages.error(request, 'Profile not found.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


def visitor_restricted(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        try:
            if request.user.profile.role == 'visitor':
                messages.warning(request, 'Action not allowed for visitor accounts.')
                return redirect('dashboard')
        except UserProfile.DoesNotExist:
            messages.error(request, 'Profile not found.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


# ─── Auth Views ──────────────────────────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, 'Invalid username or password.')
    return render(request, 'traffic/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f'Account created. Welcome, {user.first_name}!')
        return redirect('dashboard')
    return render(request, 'traffic/register.html', {'form': form})


# ─── Dashboard ───────────────────────────────────────────────
@login_required
def dashboard(request):
    user = request.user
    try:
        profile = user.profile
        is_admin = profile.is_admin()
    except UserProfile.DoesNotExist:
        is_admin = False

    total_vehicles = Vehicle.objects.count()
    active_incidents = IncidentReport.objects.filter(status__in=['open', 'pending']).count()
    resolved_incidents = IncidentReport.objects.filter(status='resolved').count()
    total_users = User.objects.count()
    recent_incidents = IncidentReport.objects.select_related('reported_by').order_by('-reported_at')[:5]
    recent_actions = AdminAction.objects.select_related('admin').order_by('-performed_at')[:5]

    my_vehicles = Vehicle.objects.filter(owner=user).order_by('-registered_at')[:3]
    my_incidents = IncidentReport.objects.filter(reported_by=user).order_by('-reported_at')[:3]

    # Per-user stats for non-admin views
    my_vehicle_count = Vehicle.objects.filter(owner=user).count()
    my_vehicle_pending = Vehicle.objects.filter(owner=user, status='pending').count()
    my_incident_open = IncidentReport.objects.filter(reported_by=user, status='open').count()
    my_incident_pending = IncidentReport.objects.filter(reported_by=user, status='pending').count()
    my_incident_resolved = IncidentReport.objects.filter(reported_by=user, status='resolved').count()

    ctx = {
        'total_vehicles': total_vehicles,
        'active_incidents': active_incidents,
        'resolved_incidents': resolved_incidents,
        'total_users': total_users,
        'recent_incidents': recent_incidents,
        'recent_actions': recent_actions,
        'my_vehicles': my_vehicles,
        'my_incidents': my_incidents,
        'my_vehicle_count': my_vehicle_count,
        'my_vehicle_pending': my_vehicle_pending,
        'my_incident_open': my_incident_open,
        'my_incident_pending': my_incident_pending,
        'my_incident_resolved': my_incident_resolved,
        'is_admin': is_admin,
    }
    return render(request, 'traffic/dashboard.html', ctx)


# ─── Vehicle Views ───────────────────────────────────────────
@login_required
def vehicle_list(request):
    q = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    try:
        is_admin = request.user.profile.is_admin()
    except UserProfile.DoesNotExist:
        is_admin = False

    if is_admin:
        vehicles = Vehicle.objects.select_related('owner').all()
    else:
        vehicles = Vehicle.objects.filter(owner=request.user)

    if q:
        vehicles = vehicles.filter(
            Q(plate_number__icontains=q) |
            Q(make__icontains=q) |
            Q(model__icontains=q) |
            Q(owner__first_name__icontains=q) |
            Q(owner__last_name__icontains=q)
        )
    if status_filter:
        vehicles = vehicles.filter(status=status_filter)

    return render(request, 'traffic/vehicle_list.html', {
        'vehicles': vehicles, 'q': q, 'status_filter': status_filter, 'is_admin': is_admin
    })


@login_required
@visitor_restricted
def vehicle_register(request):
    form = VehicleForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        vehicle = form.save(commit=False)
        vehicle.owner = request.user
        vehicle.status = 'pending'
        vehicle.save()
        messages.success(request, f'Vehicle {vehicle.plate_number} submitted for approval.')
        return redirect('vehicle_list')
    return render(request, 'traffic/vehicle_form.html', {'form': form, 'title': 'Register Vehicle'})


@login_required
def vehicle_detail(request, pk):
    try:
        is_admin = request.user.profile.is_admin()
    except UserProfile.DoesNotExist:
        is_admin = False

    if is_admin:
        vehicle = get_object_or_404(Vehicle, pk=pk)
    else:
        vehicle = get_object_or_404(Vehicle, pk=pk, owner=request.user)

    status_form = VehicleStatusForm(instance=vehicle)
    if request.method == 'POST' and is_admin:
        status_form = VehicleStatusForm(request.POST, instance=vehicle)
        if status_form.is_valid():
            old_status = vehicle.status
            status_form.save()
            action_label = 'vehicle_approved' if vehicle.status == 'active' else 'vehicle_suspended'
            AdminAction.objects.create(
                admin=request.user,
                action=action_label,
                description=f'Vehicle {vehicle.plate_number} status changed from {old_status} to {vehicle.status}.'
            )
            messages.success(request, f'Vehicle status updated to {vehicle.get_status_display()}.')
            return redirect('vehicle_detail', pk=pk)
    return render(request, 'traffic/vehicle_detail.html', {
        'vehicle': vehicle, 'status_form': status_form, 'is_admin': is_admin
    })


@login_required
def vehicle_edit(request, pk):
    try:
        is_admin = request.user.profile.is_admin()
    except UserProfile.DoesNotExist:
        is_admin = False

    if is_admin:
        vehicle = get_object_or_404(Vehicle, pk=pk)
    else:
        vehicle = get_object_or_404(Vehicle, pk=pk, owner=request.user)

    form = VehicleForm(request.POST or None, instance=vehicle)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Vehicle record updated.')
        return redirect('vehicle_detail', pk=pk)
    return render(request, 'traffic/vehicle_form.html', {'form': form, 'title': 'Edit Vehicle', 'vehicle': vehicle})


# ─── Incident Report Views ───────────────────────────────────
@login_required
def incident_list(request):
    q = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    type_filter = request.GET.get('type', '')
    try:
        is_admin = request.user.profile.is_admin()
    except UserProfile.DoesNotExist:
        is_admin = False

    if is_admin:
        incidents = IncidentReport.objects.select_related('reported_by').all()
    else:
        incidents = IncidentReport.objects.filter(reported_by=request.user)

    if q:
        incidents = incidents.filter(
            Q(description__icontains=q) |
            Q(vehicle_plate__icontains=q) |
            Q(location__icontains=q)
        )
    if status_filter:
        incidents = incidents.filter(status=status_filter)
    if type_filter:
        incidents = incidents.filter(incident_type=type_filter)

    open_count = IncidentReport.objects.filter(status='open').count()
    pending_count = IncidentReport.objects.filter(status='pending').count()
    resolved_count = IncidentReport.objects.filter(status='resolved').count()

    return render(request, 'traffic/incident_list.html', {
        'incidents': incidents, 'q': q,
        'status_filter': status_filter, 'type_filter': type_filter,
        'open_count': open_count, 'pending_count': pending_count,
        'resolved_count': resolved_count, 'is_admin': is_admin,
        'status_choices': IncidentReport.STATUS_CHOICES,
        'type_choices': IncidentReport.INCIDENT_TYPE_CHOICES,
    })


@login_required
def incident_report(request):
    form = IncidentReportForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        incident = form.save(commit=False)
        incident.reported_by = request.user
        incident.save()
        messages.success(request, f'Incident #{incident.pk} reported successfully.')
        return redirect('incident_list')
    return render(request, 'traffic/incident_form.html', {'form': form})


@login_required
def incident_detail(request, pk):
    try:
        is_admin = request.user.profile.is_admin()
    except UserProfile.DoesNotExist:
        is_admin = False

    if is_admin:
        incident = get_object_or_404(IncidentReport, pk=pk)
    else:
        incident = get_object_or_404(IncidentReport, pk=pk, reported_by=request.user)

    resolve_form = ResolveIncidentForm(instance=incident)
    if request.method == 'POST' and is_admin:
        resolve_form = ResolveIncidentForm(request.POST, instance=incident)
        if resolve_form.is_valid():
            inc = resolve_form.save(commit=False)
            if inc.status == 'resolved' and not inc.resolved_at:
                inc.resolved_at = timezone.now()
            inc.save()
            AdminAction.objects.create(
                admin=request.user,
                action='incident_resolved',
                description=f'Incident #{incident.pk} ({incident.get_incident_type_display()}) updated to {incident.get_status_display()}.'
            )
            messages.success(request, 'Incident updated.')
            return redirect('incident_detail', pk=pk)

    return render(request, 'traffic/incident_detail.html', {
        'incident': incident, 'resolve_form': resolve_form, 'is_admin': is_admin
    })


# ─── Admin: User Management ──────────────────────────────────
@login_required
@admin_required
def user_list(request):
    q = request.GET.get('q', '')
    users = User.objects.select_related('profile').all()
    if q:
        users = users.filter(
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(username__icontains=q) |
            Q(email__icontains=q)
        )
    return render(request, 'traffic/user_list.html', {'users': users, 'q': q})


@login_required
@admin_required
def user_detail(request, pk):
    target_user = get_object_or_404(User, pk=pk)
    try:
        profile = target_user.profile
    except UserProfile.DoesNotExist:
        profile = None

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'toggle_active':
            target_user.is_active = not target_user.is_active
            target_user.save()
            label = 'user_activated' if target_user.is_active else 'user_suspended'
            AdminAction.objects.create(
                admin=request.user,
                action=label,
                description=f'User {target_user.username} set to {"active" if target_user.is_active else "suspended"}.'
            )
            messages.success(request, f'User {"activated" if target_user.is_active else "suspended"}.')
        return redirect('user_detail', pk=pk)

    vehicles = Vehicle.objects.filter(owner=target_user)
    incidents = IncidentReport.objects.filter(reported_by=target_user)
    return render(request, 'traffic/user_detail.html', {
        'target_user': target_user, 'profile': profile,
        'vehicles': vehicles, 'incidents': incidents
    })


# ─── Admin: Reports ──────────────────────────────────────────
@login_required
@admin_required
def reports_view(request):
    from django.db.models import Count
    total_vehicles = Vehicle.objects.count()
    pending_vehicles = Vehicle.objects.filter(status='pending').count()
    active_vehicles = Vehicle.objects.filter(status='active').count()
    total_incidents = IncidentReport.objects.count()
    open_incidents = IncidentReport.objects.filter(status='open').count()
    resolved_incidents = IncidentReport.objects.filter(status='resolved').count()
    total_users = User.objects.count()
    recent_actions = AdminAction.objects.select_related('admin').all()[:10]

    incident_by_type = IncidentReport.objects.values('incident_type').annotate(count=Count('id')).order_by('-count')
    incident_by_location = IncidentReport.objects.values('location').annotate(count=Count('id')).order_by('-count')
    vehicles_by_category = Vehicle.objects.values('category').annotate(count=Count('id')).order_by('-count')

    ctx = {
        'total_vehicles': total_vehicles,
        'pending_vehicles': pending_vehicles,
        'active_vehicles': active_vehicles,
        'total_incidents': total_incidents,
        'open_incidents': open_incidents,
        'resolved_incidents': resolved_incidents,
        'total_users': total_users,
        'recent_actions': recent_actions,
        'incident_by_type': incident_by_type,
        'incident_by_location': incident_by_location,
        'vehicles_by_category': vehicles_by_category,
    }
    return render(request, 'traffic/reports.html', ctx)
