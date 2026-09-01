from django.urls import path
from .views import (
    RegisterView, LoginView, MeView,
    HMDashboardView, MEODashboardView,
    ResultSubmissionListCreateView, ResultSubmissionDetailView,
    RankingListView,
    MandalListView, SchoolListView,
    get_dashboard_stats,
)
from . import views

app_name = 'api'

urlpatterns = [
    # Authentication
    path('auth/register', RegisterView.as_view(), name='register'),
    path('auth/login', LoginView.as_view(), name='login'),
    path('auth/me', MeView.as_view(), name='auth-me'),

    # Dashboards
    path('dashboard/hm', HMDashboardView.as_view(), name='hm-dashboard'),
    path('dashboard/meo', MEODashboardView.as_view(), name='meo-dashboard'),
    path('dashboard/stats', get_dashboard_stats, name='dashboard-stats'),

    # Result submissions
    path('submissions', ResultSubmissionListCreateView.as_view(), name='submission-list'),
    path('submissions/<int:pk>', ResultSubmissionDetailView.as_view(), name='submission-detail'),

    # Rankings
    path('rankings', RankingListView.as_view(), name='ranking-list'),

    # Reference data (for dropdowns)
    path('mandals', MandalListView.as_view(), name='mandal-list'),
    path('schools', SchoolListView.as_view(), name='school-list'),
]
