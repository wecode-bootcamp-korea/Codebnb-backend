from django.urls import path
from .views import GoogleLoginVIew, FacebookLoginView, TripStateView

urlpatterns = [
    path('google', GoogleLoginVIew.as_view()),
    path('facebook', FacebookLoginView.as_view()),
    path('tripstate', TripStateView.as_view()),
]