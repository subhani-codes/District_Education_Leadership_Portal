from rest_framework import generics, permissions, serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Mandal, School, Headmaster, MandalEducationOfficer, ResultSubmission, RankingSnapshot
from .serializers import (
    UserSerializer, HeadmasterSerializer, MandalEducationOfficerSerializer,
    DistrictEducationOfficerSerializer,
    DistrictSerializer, MandalSerializer, SchoolSerializer,
    ResultSubmissionSerializer, RankingSnapshotSerializer
)

User = get_user_model()

# Authentication Views
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserSerializer


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            email = request.data.get('email')
            password = request.data.get('password')

            user = User.objects.filter(email=email).first()

            if user is not None and user.check_password(password):
                from rest_framework.authtoken.models import Token
                token, created = Token.objects.get_or_create(user=user)

                return Response({
                    'user_id': user.id,
                    'email': user.email,
                    'name': user.get_full_name(),
                    'role': user.role,
                    'token': token.key
                })
            else:
                return Response(
                    {'error': 'Invalid credentials'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        except Exception as e:
            return Response(
                {'error': f'Internal Server Error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MeView(APIView):
    """Return the authenticated user's basic profile (used by the frontend on app load)."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        u = request.user
        return Response({
            'user_id': u.id,
            'email': u.email,
            'name': u.get_full_name(),
            'role': u.role,
        })


# Dashboard Views
class HMDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            headmaster = Headmaster.objects.get(user=request.user)
        except Headmaster.DoesNotExist:
            return Response(
                {'error': 'Headmaster profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get recent result submissions
        recent_submissions = ResultSubmission.objects.filter(
            headmaster=headmaster
        ).select_related('school').order_by('-submitted_at')[:5]

        # Get current ranking
        latest_ranking = RankingSnapshot.objects.filter(
            school=headmaster.school,
            academic_year='2024'  # Should be dynamic based on current year
        ).first()

        # Calculate statistics
        total_submissions = ResultSubmission.objects.filter(
            headmaster=headmaster
        ).count()

        approved_submissions = ResultSubmission.objects.filter(
            headmaster=headmaster,
            status=ResultSubmission.Status.APPROVED
        ).count()

        data = {
            'headmaster': HeadmasterSerializer(headmaster).data,
            'recent_submissions': ResultSubmissionSerializer(recent_submissions, many=True).data,
            'current_ranking': RankingSnapshotSerializer(latest_ranking).data if latest_ranking else None,
            'statistics': {
                'total_submissions': total_submissions,
                'approved_submissions': approved_submissions,
                'pending_submissions': total_submissions - approved_submissions,
            }
        }

        return Response(data)


class MEODashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            meo = MandalEducationOfficer.objects.get(user=request.user)
        except MandalEducationOfficer.DoesNotExist:
            return Response(
                {'error': 'MEO profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get pending submissions for verification
        pending_submissions = ResultSubmission.objects.filter(
            school__mandal=meo.mandal,
            status=ResultSubmission.Status.PENDING
        ).select_related('school', 'headmaster').order_by('submitted_at')

        # Get mandal statistics
        total_schools = School.objects.filter(mandal=meo.mandal).count()
        total_hms = Headmaster.objects.filter(school__mandal=meo.mandal).count()

        # Get recent approved submissions
        recent_approved = ResultSubmission.objects.filter(
            school__mandal=meo.mandal,
            status=ResultSubmission.Status.APPROVED
        ).select_related('school', 'headmaster').order_by('-reviewed_at')[:5]

        # Calculate mandal average qualifying percentage
        mandal_approved = ResultSubmission.objects.filter(
            school__mandal=meo.mandal,
            status=ResultSubmission.Status.APPROVED
        )

        avg_qualifying_percentage = 0
        if mandal_approved.exists():
            total_percentage = sum(
                submission.qualifying_percentage or 0
                for submission in mandal_approved
            )
            avg_qualifying_percentage = round(total_percentage / mandal_approved.count(), 2)

        data = {
            'meo': MandalEducationOfficerSerializer(meo).data,
            'pending_submissions_count': pending_submissions.count(),
            'mandal_statistics': {
                'total_schools': total_schools,
                'total_hms': total_hms,
                'pending_submissions': pending_submissions.count(),
                'average_qualifying_percentage': avg_qualifying_percentage,
            },
            'recent_approved_submissions': ResultSubmissionSerializer(recent_approved, many=True).data,
        }

        return Response(data)


# Result Submission Views
class ResultSubmissionListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ResultSubmissionSerializer

    def get_queryset(self):
        # HMs can see their own submissions, MEOs can see submissions in their mandal
        user = self.request.user

        if user.is_headmaster():
            try:
                headmaster = Headmaster.objects.get(user=user)
                return ResultSubmission.objects.filter(headmaster=headmaster)
            except Headmaster.DoesNotExist:
                return ResultSubmission.objects.none()

        elif user.is_meo():
            try:
                meo = MandalEducationOfficer.objects.get(user=user)
                return ResultSubmission.objects.filter(school__mandal=meo.mandal)
            except MandalEducationOfficer.DoesNotExist:
                return ResultSubmission.objects.none()

        return ResultSubmission.objects.none()

    def perform_create(self, serializer):
        # Set the headmaster from the authenticated user
        try:
            headmaster = Headmaster.objects.get(user=self.request.user)
            serializer.save(headmaster=headmaster)
        except Headmaster.DoesNotExist:
            raise serializers.ValidationError("Headmaster profile not found")


class ResultSubmissionDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ResultSubmissionSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_headmaster():
            try:
                headmaster = Headmaster.objects.get(user=user)
                return ResultSubmission.objects.filter(headmaster=headmaster)
            except Headmaster.DoesNotExist:
                return ResultSubmission.objects.none()

        elif user.is_meo():
            try:
                meo = MandalEducationOfficer.objects.get(user=user)
                return ResultSubmission.objects.filter(school__mandal=meo.mandal)
            except MandalEducationOfficer.DoesNotExist:
                return ResultSubmission.objects.none()

        return ResultSubmission.objects.none()

    def update(self, request, *args, **kwargs):
        submission = self.get_object()

        # Only MEOs can approve/reject submissions
        if request.user.is_meo():
            try:
                meo = MandalEducationOfficer.objects.get(user=request.user)

                if 'status' in request.data:
                    status = request.data['status']
                    comment = request.data.get('reviewer_comment', '')

                    if status == ResultSubmission.Status.APPROVED:
                        submission.approve(meo, comment)
                    elif status == ResultSubmission.Status.REJECTED:
                        submission.reject(meo, comment)
                    else:
                        submission.status = status
                        submission.save()

                    return Response(ResultSubmissionSerializer(submission).data)
                else:
                    return super().update(request, *args, **kwargs)
            except MandalEducationOfficer.DoesNotExist:
                return Response(
                    {'error': 'MEO profile not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            return Response(
                {'error': 'Only MEOs can approve/reject submissions'},
                status=status.HTTP_403_FORBIDDEN
            )


# Ranking Views
class RankingListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RankingSnapshotSerializer

    def get_queryset(self):
        user = self.request.user
        academic_year = self.request.query_params.get('academic_year', '2024')
        mandal_id = self.request.query_params.get('mandal')

        qs = RankingSnapshot.objects.filter(academic_year=academic_year)

        if mandal_id:
            qs = qs.filter(school__mandal_id=mandal_id)

        if user.is_headmaster():
            try:
                headmaster = Headmaster.objects.get(user=user)
                # HMs only see their own school's row
                return qs.filter(school=headmaster.school)
            except Headmaster.DoesNotExist:
                return RankingSnapshot.objects.none()

        if user.is_meo():
            try:
                meo = MandalEducationOfficer.objects.get(user=user)
                return qs.filter(school__mandal=meo.mandal)
            except MandalEducationOfficer.DoesNotExist:
                return RankingSnapshot.objects.none()

        # Admin / DEO / state see everything (filtered by query params)
        return qs


# Reference-data endpoints (read-only, used by frontend dropdowns)
class MandalListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MandalSerializer
    queryset = Mandal.objects.all().order_by('name')


class SchoolListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SchoolSerializer

    def get_queryset(self):
        qs = School.objects.select_related('mandal').order_by('name')
        mandal_id = self.request.query_params.get('mandal')
        if mandal_id:
            qs = qs.filter(mandal_id=mandal_id)
        return qs


# Utility/API Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_dashboard_stats(request):
    """Get general dashboard statistics"""
    user = request.user
    academic_year = '2024'  # Should be dynamic

    stats = {
        'total_schools': School.objects.count(),
        'total_hms': Headmaster.objects.count(),
        'total_meos': MandalEducationOfficer.objects.count(),
        'pending_submissions': ResultSubmission.objects.filter(
            status=ResultSubmission.Status.PENDING
        ).count(),
        'approved_submissions': ResultSubmission.objects.filter(
            status=ResultSubmission.Status.APPROVED
        ).count(),
        'mandals': Mandal.objects.count(),
    }

    # Add mandal-specific stats for MEOs
    if user.is_meo():
        try:
            meo = MandalEducationOfficer.objects.get(user=user)
            stats['mandal_name'] = meo.mandal.name
            stats['mandal_pending'] = ResultSubmission.objects.filter(
                school__mandal=meo.mandal,
                status=ResultSubmission.Status.PENDING
            ).count()
        except MandalEducationOfficer.DoesNotExist:
            pass

    return Response(stats)