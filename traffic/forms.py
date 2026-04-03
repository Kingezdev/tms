from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, Vehicle, IncidentReport


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES)
    matric_or_staff_id = forms.CharField(max_length=50, required=False, label='Matric No. / Staff ID')
    department = forms.CharField(max_length=100, required=False)
    phone = forms.CharField(max_length=20, required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                role=self.cleaned_data['role'],
                matric_or_staff_id=self.cleaned_data['matric_or_staff_id'],
                department=self.cleaned_data['department'],
                phone=self.cleaned_data['phone'],
            )
        return user


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['plate_number', 'vehicle_type', 'make', 'model', 'color', 'year', 'category', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_plate_number(self):
        plate = self.cleaned_data['plate_number'].upper().strip()
        return plate


class IncidentReportForm(forms.ModelForm):
    class Meta:
        model = IncidentReport
        fields = ['incident_type', 'location', 'priority', 'description', 'vehicle_plate']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class ResolveIncidentForm(forms.ModelForm):
    class Meta:
        model = IncidentReport
        fields = ['status', 'admin_note']
        widgets = {
            'admin_note': forms.Textarea(attrs={'rows': 3}),
        }


class VehicleStatusForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['status']


class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    email = forms.EmailField()

    class Meta:
        model = UserProfile
        fields = ['role', 'matric_or_staff_id', 'department', 'phone']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
