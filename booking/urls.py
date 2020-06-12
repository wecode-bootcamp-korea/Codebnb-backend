from django.urls import path

from .views import BookingView

urlpatterns = [
    path('payment', BookingView.as_view()),
]