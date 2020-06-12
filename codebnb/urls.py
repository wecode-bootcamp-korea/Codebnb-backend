from django.urls import path, include

urlpatterns = [
    path('user/', include('user.urls')),
    path('room/', include('room.urls')),
    path('api/', include('room.urls')),
    path('booking/', include('booking.urls')),
    path('api/', include('review.urls'))
]
