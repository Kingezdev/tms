from .models import IncidentReport


def sidebar_context(request):
    if request.user.is_authenticated:
        open_incidents_count = IncidentReport.objects.filter(status='open').count()
        try:
            is_admin = request.user.profile.is_admin()
        except Exception:
            is_admin = False
        return {
            'open_incidents_count': open_incidents_count,
            'is_admin': is_admin,
        }
    return {}
