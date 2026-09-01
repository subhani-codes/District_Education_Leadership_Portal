from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from accounts.models import User
from .models import (
    District, Mandal, School,
    Headmaster, MandalEducationOfficer, DistrictEducationOfficer,
    ResultSubmission, RankingSnapshot,
)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'name', 'phone', 'profile_photo', 'role',
                 'password', 'confirm_password', 'is_active', 'is_verified')
        extra_kwargs = {
            'password': {'write_only': True},
            'is_active': {'read_only': True},
            'is_verified': {'read_only': True},
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        confirm_password = validated_data.pop('confirm_password')

        if password != confirm_password:
            raise serializers.ValidationError("Passwords do not match")

        user = User.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        confirm_password = validated_data.pop('confirm_password', None)

        if password or confirm_password:
            if password != confirm_password:
                raise serializers.ValidationError("Passwords do not match")
            instance.set_password(password)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class HeadmasterSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    school_name = serializers.CharField(source='school.name', read_only=True)
    school_code = serializers.CharField(source='school.school_code', read_only=True)

    class Meta:
        model = Headmaster
        fields = ('id', 'user', 'school', 'school_name', 'school_code',
                 'qualification', 'experience_years', 'joining_date',
                 'is_current', 'awards', 'achievements')
        read_only_fields = ('user', 'school')

    def create(self, validated_data):
        # The user and school should be set from context or request
        return Headmaster.objects.create(**validated_data)


class MandalEducationOfficerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    mandal_name = serializers.CharField(source='mandal.name', read_only=True)

    class Meta:
        model = MandalEducationOfficer
        fields = ('id', 'user', 'mandal', 'mandal_name', 'employee_id',
                 'qualification', 'experience_years', 'office_location', 'office_phone')
        read_only_fields = ('user', 'mandal')


class DistrictEducationOfficerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    district_name = serializers.CharField(source='district.name', read_only=True)

    class Meta:
        model = DistrictEducationOfficer
        fields = ('id', 'user', 'district', 'district_name', 'employee_id',
                 'qualification', 'experience_years')
        read_only_fields = ('user',)


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ('id', 'name', 'code', 'state')


class MandalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mandal
        fields = ('id', 'name', 'code', 'description', 'headquarters',
                 'contact_person', 'contact_phone', 'district')


class SchoolSerializer(serializers.ModelSerializer):
    mandal_name = serializers.CharField(source='mandal.name', read_only=True)
    headmaster_name = serializers.SerializerMethodField()

    class Meta:
        model = School
        fields = ('id', 'name', 'school_code', 'mandal', 'mandal_name',
                 'address', 'school_type', 'principal_name', 'contact_person',
                 'contact_phone', 'established_year', 'total_teachers',
                 'total_students', 'headmaster_name')
        read_only_fields = ('mandal',)

    def get_headmaster_name(self, obj):
        if hasattr(obj, 'headmaster'):
            return obj.headmaster.user.get_full_name()
        return None


class ResultSubmissionSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source='school.name', read_only=True)
    school_code = serializers.CharField(source='school.school_code', read_only=True)
    headmaster_name = serializers.CharField(source='headmaster.user.get_full_name', read_only=True)
    academic_year_display = serializers.CharField(source='get_academic_year_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    qualifying_percentage = serializers.DecimalField(read_only=True, max_digits=5, decimal_places=2)

    class Meta:
        model = ResultSubmission
        fields = ('id', 'school', 'school_name', 'school_code', 'headmaster',
                 'headmaster_name', 'academic_year', 'academic_year_display',
                 'total_students_appeared', 'students_meeting_threshold',
                 'threshold_value', 'extra_credit_points', 'extra_credit_details',
                 'submitted_at', 'status', 'status_display',
                 'reviewed_by', 'reviewed_at', 'reviewer_comment',
                 'qualifying_percentage')
        read_only_fields = ('headmaster', 'submitted_at', 'reviewed_by',
                           'reviewed_at', 'reviewer_comment', 'qualifying_percentage')

    def validate(self, data):
        # Ensure students meeting threshold doesn't exceed total appeared
        if data['students_meeting_threshold'] > data['total_students_appeared']:
            raise serializers.ValidationError(
                "Students meeting threshold cannot exceed total students appeared"
            )

        # Calculate qualifying percentage
        if data['total_students_appeared'] > 0:
            percentage = (data['students_meeting_threshold'] / data['total_students_appeared']) * 100
            data['qualifying_percentage'] = round(percentage, 2)

        return data


class RankingSnapshotSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source='school.name', read_only=True)
    school_code = serializers.CharField(source='school.school_code', read_only=True)
    mandal_name = serializers.CharField(source='school.mandal.name', read_only=True)

    class Meta:
        model = RankingSnapshot
        fields = ('id', 'school', 'school_name', 'school_code', 'mandal_name',
                 'academic_year', 'qualifying_percentage', 'mandal_rank',
                 'district_rank', 'state_rank', 'computed_at')
        read_only_fields = ('school', 'computed_at')