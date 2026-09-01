from django.contrib import admin
from .models import (
    District, Mandal, School,
    Headmaster, MandalEducationOfficer, DistrictEducationOfficer,
    StateEducationOfficial, PlatformAdmin,
    ResultSubmission, RankingSnapshot,
)


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'state')
    search_fields = ('name', 'code')


@admin.register(Mandal)
class MandalAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'district', 'headquarters')
    list_filter = ('district',)
    search_fields = ('name', 'code')


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'school_code', 'mandal', 'school_type', 'total_students')
    list_filter = ('mandal', 'school_type')
    search_fields = ('name', 'school_code')


@admin.register(Headmaster)
class HeadmasterAdmin(admin.ModelAdmin):
    list_display = ('user', 'school', 'qualification', 'experience_years', 'is_current')
    list_filter = ('is_current', 'school__mandal')
    search_fields = ('user__name', 'user__email', 'school__name')


@admin.register(MandalEducationOfficer)
class MandalEducationOfficerAdmin(admin.ModelAdmin):
    list_display = ('user', 'mandal', 'employee_id', 'office_location')
    list_filter = ('mandal',)
    search_fields = ('user__name', 'user__email', 'employee_id')


@admin.register(DistrictEducationOfficer)
class DistrictEducationOfficerAdmin(admin.ModelAdmin):
    list_display = ('user', 'district', 'employee_id')
    list_filter = ('district',)
    search_fields = ('user__name', 'user__email', 'employee_id')


@admin.register(StateEducationOfficial)
class StateEducationOfficialAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'designation')
    search_fields = ('user__name', 'user__email', 'department')


@admin.register(PlatformAdmin)
class PlatformAdminAdmin(admin.ModelAdmin):
    list_display = ('user', 'department')


@admin.register(ResultSubmission)
class ResultSubmissionAdmin(admin.ModelAdmin):
    list_display = (
        'school', 'academic_year', 'total_students_appeared',
        'students_meeting_threshold', 'qualifying_percentage', 'status',
        'submitted_at', 'reviewed_by',
    )
    list_filter = ('status', 'academic_year', 'school__mandal')
    search_fields = ('school__name', 'school__school_code')
    readonly_fields = ('submitted_at', 'reviewed_at', 'qualifying_percentage')


@admin.register(RankingSnapshot)
class RankingSnapshotAdmin(admin.ModelAdmin):
    list_display = (
        'school', 'academic_year', 'qualifying_percentage',
        'mandal_rank', 'district_rank', 'state_rank', 'computed_at',
    )
    list_filter = ('academic_year', 'school__mandal')
    search_fields = ('school__name',)
    readonly_fields = ('computed_at',)
