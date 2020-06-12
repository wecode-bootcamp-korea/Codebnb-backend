from django.db import models

class Booking(models.Model):
    user            = models.ForeignKey('user.User', on_delete=models.CASCADE)
    room            = models.ForeignKey('room.Room', on_delete=models.SET_NULL, null=True)
    payment_method  = models.ForeignKey('PaymentMethod', on_delete=models.SET_NULL, null=True)
    status          = models.ForeignKey('BookingStatus', on_delete=models.SET_NULL, null=True)
    start_date      = models.DateField()
    end_date        = models.DateField()
    final_price     = models.DecimalField(max_digits=12, decimal_places=2)
    adults          = models.PositiveIntegerField()
    children        = models.PositiveIntegerField()
    infants         = models.PositiveIntegerField()
    created_at      = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.room.title + " booked by " + self.user.username
    
    class Meta:
        db_table = 'bookings'

class BookingStatus(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name  
    
    class Meta:
        db_table = 'booking_status'

class PaymentMethod(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name  
    
    class Meta:
        db_table = 'payment_methods'

class Currency(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'currencies'

