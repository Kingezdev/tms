"""
Run this AFTER migrations to populate the database with sample data:
    python seed_data.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tms.settings')
django.setup()

from django.contrib.auth.models import User
from traffic.models import UserProfile, Vehicle, IncidentReport, AdminAction
from django.utils import timezone


def run():
    print("Seeding database...")

    # Admin user
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser('admin', 'admin@psu.edu.ng', 'admin1234')
        admin.first_name = 'System'
        admin.last_name = 'Administrator'
        admin.save()
        UserProfile.objects.create(user=admin, role='admin', department='ICT Unit', phone='+2348012345678')
        print("  Created admin user (username: admin, password: admin1234)")

    # Staff user
    if not User.objects.filter(username='dr.mwangi').exists():
        staff = User.objects.create_user('dr.mwangi', 'mwangi@psu.edu.ng', 'staff1234')
        staff.first_name = 'Samuel'
        staff.last_name = 'Mwangi'
        staff.save()
        UserProfile.objects.create(user=staff, role='staff', department='Computer Science',
                                   matric_or_staff_id='STAFF-0042', phone='+2348023456789')
        print("  Created staff user (username: dr.mwangi, password: staff1234)")

    # Student user
    if not User.objects.filter(username='amina.ibrahim').exists():
        student = User.objects.create_user('amina.ibrahim', 'amina@psu.edu.ng', 'student1234')
        student.first_name = 'Amina'
        student.last_name = 'Ibrahim'
        student.save()
        UserProfile.objects.create(user=student, role='student', department='Computer Science',
                                   matric_or_staff_id='CSC/2023/045', phone='+2348034567890')
        print("  Created student user (username: amina.ibrahim, password: student1234)")

    # Visitor user
    if not User.objects.filter(username='john.visitor').exists():
        visitor = User.objects.create_user('john.visitor', 'visitor@gmail.com', 'visitor1234')
        visitor.first_name = 'John'
        visitor.last_name = 'Visitor'
        visitor.save()
        UserProfile.objects.create(user=visitor, role='visitor', phone='+2348045678901')
        print("  Created visitor user (username: john.visitor, password: visitor1234)")

    # Vehicles
    staff_user = User.objects.get(username='dr.mwangi')
    student_user = User.objects.get(username='amina.ibrahim')
    admin_user = User.objects.get(username='admin')

    if not Vehicle.objects.filter(plate_number='ABC-123-XY').exists():
        Vehicle.objects.create(plate_number='ABC-123-XY', vehicle_type='car', make='Toyota',
                               model='Corolla', color='Silver', year=2019, owner=staff_user,
                               category='staff', status='active')
        print("  Created vehicle ABC-123-XY")

    if not Vehicle.objects.filter(plate_number='DEF-456-ZA').exists():
        Vehicle.objects.create(plate_number='DEF-456-ZA', vehicle_type='motorcycle', make='Bajaj',
                               model='Boxer', color='Blue', year=2020, owner=student_user,
                               category='student', status='active')
        print("  Created vehicle DEF-456-ZA")

    if not Vehicle.objects.filter(plate_number='GHI-789-BC').exists():
        Vehicle.objects.create(plate_number='GHI-789-BC', vehicle_type='car', make='Honda',
                               model='Civic', color='Black', year=2021, owner=student_user,
                               category='student', status='pending',
                               notes='Newly acquired vehicle')
        print("  Created vehicle GHI-789-BC (pending)")

    # Incident Reports
    if IncidentReport.objects.count() == 0:
        IncidentReport.objects.create(
            incident_type='congestion', location='main_gate', priority='high',
            description='Heavy traffic buildup at the main gate during morning hours. Vehicles queuing onto the main road causing obstruction.',
            reported_by=student_user, status='open'
        )
        IncidentReport.objects.create(
            incident_type='parking', location='library',priority='normal',
            description='Several motorcycles parked illegally in front of the library entrance blocking pedestrian access.',
            vehicle_plate='DEF-456-ZA', reported_by=staff_user, status='pending',
            admin_note='Security has been notified to address the situation.'
        )
        IncidentReport.objects.create(
            incident_type='near_miss', location='science_block', priority='emergency',
            description='A near-miss accident between a motorcycle and a pedestrian at the Science Block junction. No injuries reported.',
            reported_by=student_user, status='resolved',
            resolved_at=timezone.now(), admin_note='Speed bumps to be installed at this junction.'
        )
        IncidentReport.objects.create(
            incident_type='violation', location='admin_block', priority='normal',
            description='Vehicle driving against traffic flow on the Admin Block one-way road.',
            vehicle_plate='ABC-123-XY', reported_by=student_user, status='resolved',
            resolved_at=timezone.now()
        )
        print("  Created 4 sample incident reports")

    # Admin action log
    if AdminAction.objects.count() == 0:
        AdminAction.objects.create(
            admin=admin_user, action='vehicle_approved',
            description='Vehicle ABC-123-XY (Toyota Corolla) approved for Dr. Samuel Mwangi.'
        )
        AdminAction.objects.create(
            admin=admin_user, action='incident_resolved',
            description='Incident #3 (near-miss at Science Block) resolved. Speed bumps scheduled.'
        )
        print("  Created sample admin actions")

    print("\nDone! Test accounts:")
    print("  Admin    → username: admin       password: admin1234")
    print("  Staff    → username: dr.mwangi   password: staff1234")
    print("  Student  → username: amina.ibrahim password: student1234")
    print("  Visitor  → username: john.visitor password: visitor1234")


if __name__ == '__main__':
    run()
