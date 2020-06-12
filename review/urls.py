from django.urls import path

from .views import CheckWriteView, RoomReviewView

urlpatterns = [
    path('review/<int:pk>', CheckWriteView.as_view()),
    path('review/<int:pk>/<int:host>', RoomReviewView.as_view())
]