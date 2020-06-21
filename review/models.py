from django.db import models

from room.models import Room

class Review(models.Model):
    room       = models.ForeignKey('room.Room', on_delete=models.SET_NULL, null=True)
    reviewer   = models.ForeignKey('ReviewerType', on_delete=models.SET_NULL, null=True)
    host       = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='host_reviews')
    guest      = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='guest_reviews')
    rating     = models.OneToOneField('Rating', on_delete=models.SET_NULL, null=True)
    content    = models.CharField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[:20]
    
    class Meta:
        db_table = 'reviews'

class ReviewerType(models.Model):
    name = models.CharField(max_length=20)

    class Meta:
        db_table = 'reviewer_types'

class Rating(models.Model):
    cleanliness     = models.PositiveIntegerField()
    communication   = models.PositiveIntegerField()
    check_in        = models.PositiveIntegerField()
    accuracy        = models.PositiveIntegerField()
    location        = models.PositiveIntegerField()
    value           = models.PositiveIntegerField()

    @property
    def overall_rating(self):
        return (self.cleanliness + self.communication + self.check_in + self.accuracy + self.location + self.value) / 6

    class Meta:
        db_table = 'ratings'
