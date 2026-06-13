from django.urls import path
from apps.users.views import ProfileView, UserListView, UserDetailView

urlpatterns = [
    path('profile/',    ProfileView.as_view(),      name='user-profile'),
    path('',            UserListView.as_view(),      name='user-list'),
    path('<int:pk>/',   UserDetailView.as_view(),   name='user-detail'),
]
