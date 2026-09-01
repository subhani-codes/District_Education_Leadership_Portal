from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from accounts.models import User


class District(models.Model):
    """District level administrative division"""
    name = models.CharField(_('district name'), max_length=100, unique=True)
    code = models.CharField(_('district code'), max_length=10, unique=True)
    state = models.CharField(_('state'), max_length=100, default='Andhra Pradesh')

    class Meta:
        verbose_name = _('district')
        verbose_name_plural = _('districts')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.state})"


class Mandal(models.Model):
    """Mandal (Block) level administrative division, under a District"""
    district = models.ForeignKey(
        District, on_delete=models.PROTECT, related_name='mandals', null=True, blank=True
    )
    name = models.CharField(_('mandal name'), max_length=100, unique=True)
    code = models.CharField(_('mandal code'), max_length=10, unique=True)
    description = models.TextField(_('description'), blank=True)
    headquarters = models.CharField(_('headquarters'), max_length=100, blank=True)
    contact_person = models.CharField(_('contact person'), max_length=100, blank=True)
    contact_phone = models.CharField(_('contact phone'), max_length=20, blank=True)

    class Meta:
        verbose_name = _('mandal')
        verbose_name_plural = _('mandals')
        ordering = ['name']

    def __str__(self):
        district_part = f" - {self.district.name}" if self.district else ""
        return f"{self.name} ({self.code}){district_part}"


class School(models.Model):
    """Government school under a Mandal"""
    name = models.CharField(_('school name'), max_length=200)
    school_code = models.CharField(_('school code'), max_length=20, unique=True)
    mandal = models.ForeignKey(Mandal, on_delete=models.PROTECT, related_name='schools')
    address = models.TextField(_('address'))
    school_type = models.CharField(_('school type'), max_length=50, default='secondary')
    principal_name = models.CharField(_('principal name'), max_length=100, blank=True)
    contact_person = models.CharField(_('contact person'), max_length=100, blank=True)
    contact_phone = models.CharField(_('contact phone'), max_length=20, blank=True)
    established_year = models.PositiveIntegerField(_('established year'), blank=True, null=True)
    total_teachers = models.PositiveIntegerField(_('total teachers'), default=0)
    total_students = models.PositiveIntegerField(_('total students'), default=0)

    class Meta:
        verbose_name = _('school')
        verbose_name_plural = _('schools')
        ordering = ['name']
        unique_together = ('mandal', 'school_code')

    def __str__(self):
        return f"{self.name} ({self.school_code})"


class Headmaster(models.Model):
    """Headmaster assigned to a school"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='headmaster_profile')
    school = models.OneToOneField(School, on_delete=models.CASCADE, related_name='headmaster')
    qualification = models.CharField(_('qualification'), max_length=100, blank=True)
    experience_years = models.PositiveIntegerField(_('experience years'), default=0)
    joining_date = models.DateField(_('joining date'), blank=True, null=True)
    is_current = models.BooleanField(_('is current'), default=True)
    awards = models.TextField(_('awards'), blank=True)
    achievements = models.TextField(_('achievements'), blank=True)

    class Meta:
        verbose_name = _('headmaster')
        verbose_name_plural = _('headmasters')

    def __str__(self):
        return f"HM {self.user.get_full_name()} - {self.school.name}"


class MandalEducationOfficer(models.Model):
    """Mandal Education Officer overseeing schools in a mandal"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='meo_profile')
    mandal = models.ForeignKey(Mandal, on_delete=models.CASCADE, related_name='meos')
    employee_id = models.CharField(_('employee ID'), max_length=20, unique=True)
    qualification = models.CharField(_('qualification'), max_length=100, blank=True)
    experience_years = models.PositiveIntegerField(_('experience years'), default=0)
    office_location = models.CharField(_('office location'), max_length=100, blank=True)
    office_phone = models.CharField(_('office phone'), max_length=20, blank=True)

    class Meta:
        verbose_name = _('mandal education officer')
        verbose_name_plural = _('mandal education officers')

    def __str__(self):
        return f"MEO {self.user.get_full_name()} - {self.mandal.name}"


class DistrictEducationOfficer(models.Model):
    """District Education Officer overseeing mandals"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='deo_profile')
    district = models.ForeignKey(
        District, on_delete=models.PROTECT, related_name='deos', null=True, blank=True
    )
    employee_id = models.CharField(_('employee ID'), max_length=20, unique=True)
    qualification = models.CharField(_('qualification'), max_length=100, blank=True)
    experience_years = models.PositiveIntegerField(_('experience years'), default=0)

    class Meta:
        verbose_name = _('district education officer')
        verbose_name_plural = _('district education officers')

    def __str__(self):
        district_name = self.district.name if self.district else 'unassigned'
        return f"DEO {self.user.get_full_name()} - {district_name}"


class StateEducationOfficial(models.Model):
    """State Education Department official"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='state_official_profile')
    department = models.CharField(_('department'), max_length=100)
    designation = models.CharField(_('designation'), max_length=100, blank=True)

    class Meta:
        verbose_name = _('state education official')
        verbose_name_plural = _('state education officials')

    def __str__(self):
        return f"State Official {self.user.get_full_name()} - {self.department}"


class PlatformAdmin(models.Model):
    """Platform administrator"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    department = models.CharField(_('department'), max_length=100, blank=True)
    permissions = models.JSONField(_('permissions'), default=dict, blank=True)

    class Meta:
        verbose_name = _('platform admin')
        verbose_name_plural = _('platform admins')

    def __str__(self):
        return f"Admin {self.user.get_full_name()}"


class ResultSubmission(models.Model):
    """Class 10 result submission by a school/Headmaster"""
    class AcademicYear(models.TextChoices):
        CURRENT = '2024', '2024'
        PREVIOUS = '2023', '2023'
        TWO_YEARS_AGO = '2022', '2022'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='result_submissions')
    headmaster = models.ForeignKey(Headmaster, on_delete=models.CASCADE, related_name='result_submissions')
    academic_year = models.CharField(_('academic year'), max_length=4, choices=AcademicYear.choices)
    total_students_appeared = models.PositiveIntegerField(_('total students appeared'))
    students_meeting_threshold = models.PositiveIntegerField(
        _('students meeting threshold'),
        validators=[MinValueValidator(0)]
    )
    threshold_value = models.PositiveIntegerField(_('threshold value'), help_text=_('e.g., 500 out of 600'))
    extra_credit_points = models.PositiveIntegerField(_('extra credit points'), default=0)
    extra_credit_details = models.TextField(_('extra credit details'), blank=True)
    submitted_at = models.DateTimeField(_('submitted at'), auto_now_add=True)
    status = models.CharField(_('status'), max_length=20, choices=Status.choices, default=Status.PENDING)

    # Verification fields
    reviewed_by = models.ForeignKey(
        MandalEducationOfficer,
        on_delete=models.SET_NULL,
        related_name='reviewed_submissions',
        null=True,
        blank=True
    )
    reviewed_at = models.DateTimeField(_('reviewed at'), blank=True, null=True)
    reviewer_comment = models.TextField(_('reviewer comment'), blank=True)

    # Ranking calculation fields
    qualifying_percentage = models.DecimalField(
        _('qualifying percentage'),
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        help_text=_('Calculated: (students_meeting_threshold / total_students_appeared) × 100')
    )

    class Meta:
        verbose_name = _('result submission')
        verbose_name_plural = _('result submissions')
        ordering = ['-submitted_at']
        unique_together = ('school', 'academic_year')

    def __str__(self):
        return f"{self.school.name} - {self.academic_year} - {self.get_status_display()}"

    def calculate_qualifying_percentage(self):
        if self.total_students_appeared > 0:
            percentage = (self.students_meeting_threshold / self.total_students_appeared) * 100
            return round(percentage, 2)
        return 0

    def save(self, *args, **kwargs):
        # Calculate qualifying percentage before saving
        self.qualifying_percentage = self.calculate_qualifying_percentage()
        super().save(*args, **kwargs)

    def approve(self, reviewer, comment=''):
        from django.utils import timezone
        self.status = self.Status.APPROVED
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.reviewer_comment = comment
        self.save()
        # Trigger ranking recalculation
        self.calculate_rankings()

    def reject(self, reviewer, comment=''):
        from django.utils import timezone
        self.status = self.Status.REJECTED
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.reviewer_comment = comment
        self.save()

    def calculate_rankings(self):
        """Calculate and store rankings for this submission"""
        # Get all approved submissions for the same mandal and year
        submissions = ResultSubmission.objects.filter(
            school__mandal=self.school.mandal,
            academic_year=self.academic_year,
            status=ResultSubmission.Status.APPROVED
        )

        # Calculate rankings
        for submission in submissions:
            ranking, created = RankingSnapshot.objects.update_or_create(
                school=submission.school,
                academic_year=submission.academic_year,
                defaults={
                    'qualifying_percentage': submission.qualifying_percentage,
                    'mandal_rank': None  # Will be set after all calculations
                }
            )

        # Set ranks based on qualifying percentage (higher is better)
        ranked_submissions = submissions.order_by('-qualifying_percentage')
        for index, submission in enumerate(ranked_submissions):
            ranking = RankingSnapshot.objects.get(
                school=submission.school,
                academic_year=submission.academic_year
            )
            ranking.mandal_rank = index + 1
            ranking.save()


class RankingSnapshot(models.Model):
    """Stored ranking for a school in a given academic year"""
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='rankings')
    academic_year = models.CharField(_('academic year'), max_length=4)
    qualifying_percentage = models.DecimalField(
        _('qualifying percentage'),
        max_digits=5,
        decimal_places=2
    )
    mandal_rank = models.PositiveIntegerField(_('mandal rank'), null=True, blank=True)
    district_rank = models.PositiveIntegerField(_('district rank'), null=True, blank=True)
    state_rank = models.PositiveIntegerField(_('state rank'), null=True, blank=True)
    computed_at = models.DateTimeField(_('computed at'), auto_now_add=True)

    class Meta:
        verbose_name = _('ranking snapshot')
        verbose_name_plural = _('ranking snapshots')
        ordering = ['academic_year', 'mandal_rank']
        unique_together = ('school', 'academic_year')

    def __str__(self):
        return f"{self.school.name} - {self.academic_year} - Rank: {self.mandal_rank or 'N/R'}"