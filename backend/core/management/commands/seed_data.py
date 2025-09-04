from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
import random

from core.models import (
    Room, Attendance, Complaint, Payment, Feedback, RoomAllocation,
    Notice, MaintenanceRequest
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed the database with sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            self.clear_data()

        self.stdout.write('Seeding database with sample data...')
        
        # Create users
        self.create_users()
        
        # Create rooms
        self.create_rooms()
        
        # Create room allocations
        self.create_room_allocations()
        
        # Create payments
        self.create_payments()
        
        # Create complaints
        self.create_complaints()
        
        # Create feedback
        self.create_feedback()
        
        # Create attendance records
        self.create_attendance()
        
        # Create notices
        self.create_notices()
        
        # Create maintenance requests
        self.create_maintenance_requests()

        self.stdout.write(
            self.style.SUCCESS('Successfully seeded database with sample data!')
        )

    def clear_data(self):
        """Clear existing data"""
        User.objects.filter(is_superuser=False).delete()
        Room.objects.all().delete()
        Payment.objects.all().delete()
        Complaint.objects.all().delete()
        Feedback.objects.all().delete()
        Attendance.objects.all().delete()
        Notice.objects.all().delete()
        MaintenanceRequest.objects.all().delete()
        RoomAllocation.objects.all().delete()

    def create_users(self):
        """Create sample users"""
        self.stdout.write('Creating users...')
        
        # Create admin user
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@smartstay.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
                'phone_number': '9876543210',
                'email_verified': True,
                'phone_verified': True
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()

        # Create warden user
        warden, created = User.objects.get_or_create(
            username='warden',
            defaults={
                'email': 'warden@smartstay.com',
                'first_name': 'John',
                'last_name': 'Warden',
                'role': 'warden',
                'phone_number': '9876543211',
                'email_verified': True,
                'phone_verified': True
            }
        )
        if created:
            warden.set_password('warden123')
            warden.save()

        # Create student users
        student_names = [
            ('Alice', 'Johnson', 'alice.johnson'),
            ('Bob', 'Smith', 'bob.smith'),
            ('Charlie', 'Brown', 'charlie.brown'),
            ('Diana', 'Wilson', 'diana.wilson'),
            ('Eve', 'Davis', 'eve.davis'),
            ('Frank', 'Miller', 'frank.miller'),
            ('Grace', 'Garcia', 'grace.garcia'),
            ('Henry', 'Martinez', 'henry.martinez'),
            ('Ivy', 'Anderson', 'ivy.anderson'),
            ('Jack', 'Taylor', 'jack.taylor'),
            ('Kate', 'Thomas', 'kate.thomas'),
            ('Leo', 'Hernandez', 'leo.hernandez'),
            ('Maya', 'Moore', 'maya.moore'),
            ('Noah', 'Martin', 'noah.martin'),
            ('Olivia', 'Jackson', 'olivia.jackson'),
            ('Paul', 'Thompson', 'paul.thompson'),
            ('Quinn', 'White', 'quinn.white'),
            ('Ruby', 'Lopez', 'ruby.lopez'),
            ('Sam', 'Lee', 'sam.lee'),
            ('Tina', 'Gonzalez', 'tina.gonzalez')
        ]

        for first_name, last_name, username in student_names:
            student, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@student.com',
                    'first_name': first_name,
                    'last_name': last_name,
                    'role': 'student',
                    'phone_number': f'9{random.randint(100000000, 999999999)}',
                    'date_of_birth': date(1995, random.randint(1, 12), random.randint(1, 28)),
                    'address': f'{random.randint(1, 999)} {random.choice(["Main St", "Oak Ave", "Pine Rd", "Elm St"])}',
                    'emergency_contact': f'8{random.randint(100000000, 999999999)}',
                    'email_verified': random.choice([True, True, True, False]),  # 75% verified
                    'phone_verified': random.choice([True, True, False])  # 67% verified
                }
            )
            if created:
                student.set_password('student123')
                student.save()

    def create_rooms(self):
        """Create sample rooms"""
        self.stdout.write('Creating rooms...')
        
        room_types = ['single', 'double', 'triple', 'quad']
        floors = [1, 2, 3, 4, 5]
        
        room_number = 101
        for floor in floors:
            for room_type in room_types:
                for i in range(5):  # 5 rooms per type per floor
                    room, created = Room.objects.get_or_create(
                        number=str(room_number),
                        defaults={
                            'capacity': {'single': 1, 'double': 2, 'triple': 3, 'quad': 4}[room_type],
                            'floor': floor,
                            'room_type': room_type,
                            'status': random.choice(['available', 'occupied', 'maintenance']),
                            'monthly_rent': Decimal(random.randint(3000, 8000)),
                            'amenities': random.choice([
                                'WiFi, AC, Study Table',
                                'WiFi, AC, Study Table, Wardrobe',
                                'WiFi, AC, Study Table, Wardrobe, Mini Fridge',
                                'WiFi, AC, Study Table, Wardrobe, Mini Fridge, TV'
                            ]),
                            'description': f'Comfortable {room_type} room on floor {floor} with modern amenities'
                        }
                    )
                    room_number += 1

    def create_room_allocations(self):
        """Create sample room allocations"""
        self.stdout.write('Creating room allocations...')
        
        students = User.objects.filter(role='student')
        rooms = Room.objects.all()
        
        # Allocate rooms to some students
        for student in students[:15]:  # Allocate to first 15 students
            room = random.choice(rooms)
            start_date = date.today() - timedelta(days=random.randint(30, 365))
            
            allocation, created = RoomAllocation.objects.get_or_create(
                user=student,
                room=room,
                start_date=start_date,
                defaults={
                    'status': 'active',
                    'monthly_rent': room.monthly_rent,
                    'security_deposit': room.monthly_rent * 2
                }
            )

    def create_payments(self):
        """Create sample payments"""
        self.stdout.write('Creating payments...')
        
        students = User.objects.filter(role='student')
        payment_types = ['rent', 'security', 'maintenance', 'penalty', 'other']
        
        for student in students:
            # Create some payments for each student
            for i in range(random.randint(2, 8)):
                payment = Payment.objects.create(
                    user=student,
                    amount=Decimal(random.randint(1000, 10000)),
                    payment_type=random.choice(payment_types),
                    status=random.choice(['pending', 'success', 'failed']),
                    due_date=date.today() + timedelta(days=random.randint(-30, 30)),
                    description=f'{random.choice(payment_types).title()} payment'
                )
                
                if payment.status == 'success':
                    payment.paid_date = timezone.now() - timedelta(days=random.randint(1, 30))

    def create_complaints(self):
        """Create sample complaints"""
        self.stdout.write('Creating complaints...')
        
        students = User.objects.filter(role='student')
        rooms = Room.objects.all()
        
        complaint_titles = [
            'Broken AC',
            'Water leakage',
            'WiFi issues',
            'Noisy neighbors',
            'Power outage',
            'Broken door lock',
            'Plumbing problem',
            'Internet connectivity',
            'Room cleaning required',
            'Furniture damage'
        ]
        
        for i in range(20):
            student = random.choice(students)
            room = random.choice(rooms)
            
            complaint = Complaint.objects.create(
                user=student,
                room=room,
                title=random.choice(complaint_titles),
                description=f'Detailed description of the {random.choice(complaint_titles).lower()} issue',
                status=random.choice(['open', 'in_progress', 'resolved'])
            )

    def create_feedback(self):
        """Create sample feedback"""
        self.stdout.write('Creating feedback...')
        
        students = User.objects.filter(role='student')
        categories = ['general', 'facilities', 'staff', 'food', 'security', 'maintenance']
        
        feedback_comments = [
            'Great hostel with excellent facilities',
            'Good experience overall',
            'Could be better',
            'Excellent staff and services',
            'Room was clean and comfortable',
            'WiFi speed could be improved',
            'Food quality is good',
            'Security is adequate',
            'Maintenance response is quick',
            'Overall satisfied with the hostel'
        ]
        
        for student in students:
            for i in range(random.randint(1, 3)):
                feedback = Feedback.objects.create(
                    user=student,
                    rating=random.randint(1, 5),
                    comments=random.choice(feedback_comments),
                    category=random.choice(categories),
                    is_anonymous=random.choice([True, False])
                )

    def create_attendance(self):
        """Create sample attendance records"""
        self.stdout.write('Creating attendance records...')
        
        students = User.objects.filter(role='student')
        
        # Create attendance for the last 30 days
        for i in range(30):
            attendance_date = date.today() - timedelta(days=i)
            
            for student in students:
                attendance, created = Attendance.objects.get_or_create(
                    user=student,
                    date=attendance_date,
                    defaults={
                        'present': random.choice([True, True, True, False])  # 75% attendance
                    }
                )

    def create_notices(self):
        """Create sample notices"""
        self.stdout.write('Creating notices...')
        
        admin = User.objects.filter(role='admin').first()
        warden = User.objects.filter(role='warden').first()
        
        notices_data = [
            {
                'title': 'Hostel Rules and Regulations',
                'content': 'Please follow all hostel rules and regulations. Violations may result in disciplinary action.',
                'priority': 'high',
                'target_audience': 'student'
            },
            {
                'title': 'Monthly Maintenance Schedule',
                'content': 'Monthly maintenance will be conducted on the first Sunday of every month.',
                'priority': 'medium',
                'target_audience': 'student'
            },
            {
                'title': 'Payment Due Reminder',
                'content': 'Monthly rent payments are due by the 5th of each month. Late fees will apply.',
                'priority': 'urgent',
                'target_audience': 'student'
            },
            {
                'title': 'WiFi Maintenance',
                'content': 'WiFi services will be temporarily unavailable on Sunday from 2 AM to 4 AM for maintenance.',
                'priority': 'medium',
                'target_audience': 'student'
            },
            {
                'title': 'Security Update',
                'content': 'New security cameras have been installed. Please report any suspicious activities.',
                'priority': 'high',
                'target_audience': 'student'
            }
        ]
        
        for notice_data in notices_data:
            created_by = random.choice([admin, warden])
            if created_by:
                notice = Notice.objects.create(
                    created_by=created_by,
                    **notice_data
                )

    def create_maintenance_requests(self):
        """Create sample maintenance requests"""
        self.stdout.write('Creating maintenance requests...')
        
        students = User.objects.filter(role='student')
        rooms = Room.objects.all()
        
        maintenance_titles = [
            'AC Repair',
            'Plumbing Issue',
            'Electrical Problem',
            'Door Lock Repair',
            'Window Fix',
            'Furniture Repair',
            'WiFi Router Issue',
            'Water Heater Problem',
            'Light Fixture Repair',
            'Floor Tile Replacement'
        ]
        
        for i in range(15):
            student = random.choice(students)
            room = random.choice(rooms)
            
            maintenance = MaintenanceRequest.objects.create(
                user=student,
                room=room,
                title=random.choice(maintenance_titles),
                description=f'Detailed description of the {random.choice(maintenance_titles).lower()} issue',
                priority=random.choice(['low', 'medium', 'high', 'urgent']),
                status=random.choice(['pending', 'in_progress', 'completed']),
                estimated_cost=Decimal(random.randint(500, 5000))
            )
            
            if maintenance.status == 'completed':
                maintenance.actual_cost = maintenance.estimated_cost + Decimal(random.randint(-500, 1000))
                maintenance.completed_at = timezone.now() - timedelta(days=random.randint(1, 30))
                maintenance.save()
