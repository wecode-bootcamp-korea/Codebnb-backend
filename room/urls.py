from django.urls import path

from .views import RoomListView, RoomDetailView, MonthlyStayListView, RegisterRoomView

urlpatterns = [
    path('list', RoomListView.as_view()),
    path('monthly', MonthlyStayListView.as_view()),
    path('detail/<int:room_id>', RoomDetailView.as_view()),
    path('register/room', RegisterRoomView.as_view())
]
