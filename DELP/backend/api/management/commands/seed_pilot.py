"""
seed_pilot — populate one pilot mandal with schools, HMs, and an MEO.

Idempotent: safe to re-run. Existing rows are looked up by their natural key.

Usage:
    python manage.py seed_pilot
    python manage.py seed_pilot --reset   # delete prior pilot data first
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import User
from api.models import (
    District, Mandal, School,
    Headmaster, MandalEducationOfficer,
    ResultSubmission,
)


PILOT_DISTRICT = {'name': 'Pilot District', 'code': 'PD01', 'state': 'Andhra Pradesh'}
PILOT_MANDAL = {
    'name': 'Pilot Mandal', 'code': 'PM01',
    'headquarters': 'Pilot Town', 'contact_person': 'Demo MEO',
    'contact_phone': '9999999999',
}
PILOT_SCHOOLS = [
    {'name': 'ZPHS Pilot A', 'school_code': 'ZPHS-A', 'address': 'Pilot Village A',
     'total_students': 300, 'total_teachers': 12, 'established_year': 1985},
    {'name': 'ZPHS Pilot B', 'school_code': 'ZPHS-B', 'address': 'Pilot Village B',
     'total_students': 250, 'total_teachers': 10, 'established_year': 1992},
    {'name': 'ZPHS Pilot C', 'school_code': 'ZPHS-C', 'address': 'Pilot Village C',
     'total_students': 200, 'total_teachers': 8,  'established_year': 2001},
]
PILOT_HMS = [
    {'email': 'hm1@pilot.test',  'name': 'HM One',   'qualification': 'M.A., B.Ed',
     'experience_years': 12, 'school_code': 'ZPHS-A'},
    {'email': 'hm2@pilot.test',  'name': 'HM Two',   'qualification': 'M.Sc., B.Ed',
     'experience_years': 8,  'school_code': 'ZPHS-B'},
    {'email': 'hm3@pilot.test',  'name': 'HM Three', 'qualification': 'M.A., B.Ed',
     'experience_years': 15, 'school_code': 'ZPHS-C'},
]
PILOT_MEO = {
    'email': 'meo1@pilot.test', 'name': 'MEO One', 'employee_id': 'MEO-PD-001',
    'qualification': 'M.A., B.Ed', 'experience_years': 18,
    'office_location': 'Pilot Mandal Office', 'office_phone': '9999999999',
}
HM_PASSWORD = 'demo1234'
MEO_PASSWORD = 'demo1234'

# Demo result submissions so the MEO has something to verify on first run.
DEMO_SUBMISSIONS = [
    # (school_code, year, total, meeting_threshold, threshold_value, extra_credit, extra_details)
    ('ZPHS-A', '2024', 60, 48, 500, 5,  'Two students won district-level science fair.'),
    ('ZPHS-B', '2024', 55, 35, 500, 0,  ''),
    ('ZPHS-C', '2024', 48, 40, 500, 10, 'Athletics: 2 state medals; cultural: 1 district prize.'),
    ('ZPHS-A', '2023', 58, 30, 500, 0,  ''),
    ('ZPHS-B', '2023', 52, 28, 500, 0,  ''),
]


def _get_or_create_user(email, name, role, password):
    user, created = User.objects.get_or_create(
        email=email,
        defaults={'name': name, 'role': role, 'is_active': True, 'is_verified': True},
    )
    if created or not user.has_usable_password():
        user.set_password(password)
        user.save()
    return user


class Command(BaseCommand):
    help = 'Seed a single pilot mandal with 3 schools, 3 HMs, 1 MEO, and demo submissions.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset', action='store_true',
            help='Delete prior pilot data (users, schools, mandal) before seeding.',
        )

    @transaction.atomic
    def handle(self, *args, **opts):
        if opts['reset']:
            self.stdout.write(self.style.WARNING('--reset: removing prior pilot data...'))
            User.objects.filter(email__in=[h['email'] for h in PILOT_HMS]).delete()
            User.objects.filter(email=PILOT_MEO['email']).delete()
            School.objects.filter(school_code__in=[s['school_code'] for s in PILOT_SCHOOLS]).delete()
            Mandal.objects.filter(code=PILOT_MANDAL['code']).delete()
            District.objects.filter(code=PILOT_DISTRICT['code']).delete()

        # 1. District + Mandal
        district, _ = District.objects.get_or_create(
            code=PILOT_DISTRICT['code'], defaults=PILOT_DISTRICT,
        )
        mandal, _ = Mandal.objects.get_or_create(
            code=PILOT_MANDAL['code'],
            defaults={**PILOT_MANDAL, 'district': district},
        )

        # 2. Schools
        schools = {}
        for s in PILOT_SCHOOLS:
            school, _ = School.objects.get_or_create(
                school_code=s['school_code'],
                defaults={**s, 'mandal': mandal},
            )
            schools[s['school_code']] = school

        # 3. HMs (and their profile rows)
        hms = {}
        for h in PILOT_HMS:
            user = _get_or_create_user(h['email'], h['name'], 'hm', HM_PASSWORD)
            hm, _ = Headmaster.objects.get_or_create(
                user=user,
                defaults={
                    'school': schools[h['school_code']],
                    'qualification': h['qualification'],
                    'experience_years': h['experience_years'],
                },
            )
            hms[h['email']] = hm

        # 4. MEO
        meo_user = _get_or_create_user(PILOT_MEO['email'], PILOT_MEO['name'], 'meo', MEO_PASSWORD)
        meo_defaults = {k: v for k, v in PILOT_MEO.items() if k not in ('email', 'name')}
        meo, _ = MandalEducationOfficer.objects.get_or_create(
            user=meo_user,
            defaults={**meo_defaults, 'mandal': mandal},
        )

        # 5. Demo submissions (status PENDING — so the MEO can verify on first login)
        created_subs = 0
        for code, year, total, meeting, threshold, extra, details in DEMO_SUBMISSIONS:
            school = schools[code]
            # Find the HM for this school
            hm = next(h for h in hms.values() if h.school_id == school.id)
            _, created = ResultSubmission.objects.get_or_create(
                school=school,
                academic_year=year,
                defaults={
                    'headmaster': hm,
                    'total_students_appeared': total,
                    'students_meeting_threshold': meeting,
                    'threshold_value': threshold,
                    'extra_credit_points': extra,
                    'extra_credit_details': details,
                },
            )
            if created:
                created_subs += 1

        self.stdout.write(self.style.SUCCESS('\nPilot data ready.'))
        self.stdout.write('  District:   ' + district.name)
        self.stdout.write('  Mandal:     ' + mandal.name)
        self.stdout.write('  Schools:    ' + ', '.join(s.name for s in schools.values()))
        self.stdout.write('  HM logins:  ' + ', '.join(h['email'] for h in PILOT_HMS) + f'  (password: {HM_PASSWORD})')
        self.stdout.write('  MEO login:  ' + PILOT_MEO['email'] + f'  (password: {MEO_PASSWORD})')
        self.stdout.write(f'  New submissions created: {created_subs}')
        self.stdout.write('\nTo also create a Django superuser, run:  python manage.py createsuperuser')
