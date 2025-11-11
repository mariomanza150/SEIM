import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from accounts.models import Role, User
from documents.models import Document, DocumentType
from exchange.models import (
    Application,
    ApplicationStatus,
    Comment,
    Program,
    TimelineEvent,
)
from notifications.models import Notification, NotificationType

fake = Faker()


class Command(BaseCommand):
    help = "Create comprehensive demo data for SEIM system demonstration"

    def add_arguments(self, parser):
        parser.add_argument(
            "--users",
            type=int,
            default=20,
            help="Number of users to create (default: 20)",
        )
        parser.add_argument(
            "--programs",
            type=int,
            default=8,
            help="Number of programs to create (default: 8)",
        )
        parser.add_argument(
            "--applications",
            type=int,
            default=50,
            help="Number of applications to create (default: 50)",
        )

    def handle(self, *args, **options):
        self.stdout.write("Creating comprehensive demo data for SEIM...")

        # Create roles first
        self.create_roles()

        # Create users with profiles
        users = self.create_users(options["users"])

        # Create programs
        programs = self.create_programs(options["programs"])

        # Create applications
        applications = self.create_applications(
            users, programs, options["applications"]
        )

        # Create documents for applications
        self.create_documents(applications)

        # Create comments and timeline events
        self.create_comments_and_events(applications, users)

        # Create notifications
        self.create_notifications(users, applications)

        self.stdout.write(self.style.SUCCESS("Demo data creation completed!"))
        self.stdout.write(
            f"Created: {len(users)} users, {len(programs)} programs, {len(applications)} applications"
        )

    def create_roles(self):
        """Create roles if they don't exist."""
        roles = ["admin", "coordinator", "student"]
        for role_name in roles:
            Role.objects.get_or_create(name=role_name)

    def create_users(self, num_users):
        """Create users with different roles and profiles."""
        users = []

        # Create admin users
        admin_role = Role.objects.get(name="admin")
        for i in range(2):
            username = f"admin{i+1}"
            email = f"admin{i+1}@seim.edu"
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": email,
                    "first_name": fake.first_name(),
                    "last_name": fake.last_name(),
                    "is_email_verified": True,
                    "is_active": True,
                },
            )
            if created:
                user.set_password("admin123")
                user.save()
                self.stdout.write(f"  Created admin user: {user.username}")
            else:
                self.stdout.write(f"  Admin user already exists: {user.username}")
            user.roles.add(admin_role)
            users.append(user)

        # Create coordinator users
        coordinator_role = Role.objects.get(name="coordinator")
        for i in range(3):
            username = f"coordinator{i+1}"
            email = f"coordinator{i+1}@seim.edu"
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": email,
                    "first_name": fake.first_name(),
                    "last_name": fake.last_name(),
                    "is_email_verified": True,
                    "is_active": True,
                },
            )
            if created:
                user.set_password("coordinator123")
                user.save()
                self.stdout.write(f"  Created coordinator user: {user.username}")
            else:
                self.stdout.write(f"  Coordinator user already exists: {user.username}")
            user.roles.add(coordinator_role)
            users.append(user)

        # Create student users
        student_role = Role.objects.get(name="student")
        num_students = max(1, num_users - 5)  # Ensure at least 1 student
        for i in range(num_students):
            username = f"student{i+1}"
            email = f"student{i+1}@university.edu"
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": email,
                    "first_name": fake.first_name(),
                    "last_name": fake.last_name(),
                    "is_email_verified": True,
                    "is_active": True,
                },
            )
            if created:
                user.set_password("student123")
                user.save()
                self.stdout.write(f"  Created student user: {user.username}")
            else:
                self.stdout.write(f"  Student user already exists: {user.username}")
            user.roles.add(student_role)
            # Update profile with realistic data
            profile = user.profile
            profile.gpa = round(random.uniform(2.5, 4.0), 2)
            profile.language = random.choice(
                ["English", "Spanish", "French", "German", "Italian"]
            )
            profile.secondary_email = fake.email()
            profile.save()
            users.append(user)

        return users

    def create_programs(self, num_programs):
        """Create diverse exchange programs."""
        programs = []

        program_data = [
            {
                "name": "Erasmus+ Computer Science Exchange",
                "description": "Study computer science at top European universities through the Erasmus+ program.",
                "min_gpa": 3.0,
                "required_language": "English",
                "recurring": True,
            },
            {
                "name": "Business Administration in Spain",
                "description": "Immerse yourself in Spanish business culture while studying at prestigious Spanish universities.",
                "min_gpa": 3.2,
                "required_language": "Spanish",
                "recurring": True,
            },
            {
                "name": "Engineering Exchange in Germany",
                "description": "Study engineering at renowned German technical universities.",
                "min_gpa": 3.5,
                "required_language": "German",
                "recurring": True,
            },
            {
                "name": "Arts and Culture in France",
                "description": "Explore French arts, culture, and humanities in the heart of Paris.",
                "min_gpa": 2.8,
                "required_language": "French",
                "recurring": False,
            },
            {
                "name": "Environmental Science in Scandinavia",
                "description": "Study environmental science and sustainability in Nordic countries.",
                "min_gpa": 3.3,
                "required_language": "English",
                "recurring": True,
            },
            {
                "name": "Medical Research Exchange",
                "description": "Participate in cutting-edge medical research at leading European medical schools.",
                "min_gpa": 3.7,
                "required_language": "English",
                "recurring": False,
            },
            {
                "name": "Language Immersion in Italy",
                "description": "Intensive Italian language and cultural immersion program.",
                "min_gpa": 2.5,
                "required_language": "Italian",
                "recurring": True,
            },
            {
                "name": "Summer Research Program",
                "description": "Short-term research opportunities across various European institutions.",
                "min_gpa": 3.0,
                "required_language": "English",
                "recurring": True,
            },
        ]

        for _i, data in enumerate(program_data[:num_programs]):
            # Create programs with different dates
            start_date = timezone.now().date() + timedelta(days=random.randint(30, 365))
            end_date = start_date + timedelta(days=random.randint(90, 180))

            program = Program.objects.create(
                name=data["name"],
                description=data["description"],
                start_date=start_date,
                end_date=end_date,
                is_active=random.choice([True, True, True, False]),  # 75% active
                min_gpa=data["min_gpa"],
                required_language=data["required_language"],
                recurring=data["recurring"],
            )
            programs.append(program)
            self.stdout.write(f"  Created program: {program.name}")

        return programs

    def create_applications(self, users, programs, num_applications):
        """Create applications with realistic status distribution."""
        applications = []
        student_users = [u for u in users if u.has_role("student")]
        statuses = list(ApplicationStatus.objects.all().order_by("order"))

        for i in range(num_applications):
            student = random.choice(student_users)
            program = random.choice(programs)

            # Create application with dynamic status distribution
            # Generate weights dynamically to match the number of statuses
            num_statuses = len(statuses)
            if num_statuses == 0:
                self.stdout.write(self.style.ERROR("No application statuses found. Please run create_initial_data first."))
                return applications

            # Create more even distribution with slight preference for middle statuses
            if num_statuses == 1:
                status_weights = [1.0]
            elif num_statuses == 2:
                status_weights = [0.4, 0.6]  # Slight preference for second status
            elif num_statuses == 3:
                status_weights = [0.3, 0.4, 0.3]  # Middle status slightly more likely
            elif num_statuses == 4:
                status_weights = [0.2, 0.3, 0.3, 0.2]  # Middle statuses more likely
            elif num_statuses == 5:
                status_weights = [0.15, 0.25, 0.3, 0.25, 0.05]  # Middle statuses more likely
            elif num_statuses == 6:
                status_weights = [0.1, 0.2, 0.25, 0.25, 0.15, 0.05]  # Middle statuses more likely
            elif num_statuses == 7:
                status_weights = [0.1, 0.2, 0.25, 0.25, 0.15, 0.03, 0.02]  # Middle statuses more likely
            else:
                # For more than 7 statuses, create a more even distribution
                # with slight preference for middle statuses
                weights = []
                for i in range(num_statuses):
                    # Create a bell curve-like distribution
                    distance_from_center = abs(i - (num_statuses - 1) / 2)
                    max_distance = (num_statuses - 1) / 2
                    weight = 1.0 - (distance_from_center / max_distance) * 0.3
                    weights.append(weight)
                status_weights = weights

            status = random.choices(statuses, weights=status_weights)[0]

            application = Application.objects.create(
                program=program,
                student=student,
                status=status,
                submitted_at=timezone.now() - timedelta(days=random.randint(1, 60))
                if status.name != "draft"
                else None,
                withdrawn=status.name == "cancelled",
            )
            applications.append(application)

            if i % 10 == 0:  # Log every 10th application
                self.stdout.write(
                    f"  Created application {i+1}/{num_applications}: {student.username} -> {program.name} ({status.name})"
                )

        return applications

    def create_documents(self, applications):
        """Create documents for applications."""
        document_types = list(DocumentType.objects.all())

        for application in applications:
            # Create 1-4 documents per application
            num_docs = random.randint(1, 4)
            for _i in range(num_docs):
                doc_type = random.choice(document_types)

                Document.objects.create(
                    application=application,
                    type=doc_type,
                    uploaded_by=application.student,
                    is_valid=random.choice([True, True, False]),  # 67% valid
                    validated_at=timezone.now() - timedelta(days=random.randint(1, 30))
                    if random.choice([True, False])
                    else None,
                )

    def create_comments_and_events(self, applications, users):
        """Create comments and timeline events for applications."""
        coordinators = [u for u in users if u.has_role("coordinator")]

        for application in applications:
            # Create 0-3 comments per application
            num_comments = random.randint(0, 3)
            for _i in range(num_comments):
                author = random.choice(coordinators + [application.student])
                is_private = author.has_role("coordinator") and random.choice(
                    [True, False]
                )

                Comment.objects.create(
                    application=application,
                    author=author,
                    text=fake.paragraph(nb_sentences=random.randint(2, 5)),
                    is_private=is_private,
                    created_at=timezone.now() - timedelta(days=random.randint(1, 30)),
                )

            # Create timeline events for status changes
            if application.status.name != "draft":
                TimelineEvent.objects.create(
                    application=application,
                    event_type="status_change",
                    description=f"Application status changed to {application.status.name}",
                    created_by=random.choice(coordinators) if coordinators else None,
                    created_at=application.submitted_at or timezone.now(),
                )

    def create_notifications(self, users, applications):
        """Create notifications for users."""
        notification_types = list(NotificationType.objects.all())

        for user in users:
            # Create 0-5 notifications per user
            num_notifications = random.randint(0, 5)
            for _i in range(num_notifications):
                notif_type_choice = random.choice(['in_app', 'email', 'both'])

                Notification.objects.create(
                    recipient=user,
                    title=fake.sentence(nb_words=6),
                    message=fake.paragraph(nb_sentences=2),
                    notification_type=notif_type_choice,
                    is_read=random.choice([True, False]),
                    sent_at=timezone.now() - timedelta(days=random.randint(1, 60)),
                )
