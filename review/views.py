import json

from django.db.models   import Q
from django.http        import HttpResponse, JsonResponse
from django.views       import View


from codebnb.utils      import login_required
from codebnb.enum       import TOHOST
from review.models      import Review, ReviewerType, Rating
from user.models        import User

class CheckWriteView(View):
    @login_required
    def get(self, request, pk):
        user = request.user
        if User.objects.prefetch_related('review_set').filter(Q(id = user.id)& Q(guest_reviews__room__id = pk)).exists():
            return JsonResponse({'meesage':'Already Writ Review'}, status = 400)
        return HttpResponse(status = 200)

class RoomReviewView(View):
    @login_required
    def post(self, request, pk, host):
        user = request.user
        data = json.loads(request.body)
        rating = Rating.objects.create(
            cleanliness = data['inputs'].get('cleanliness', 0),
            communication = data['inputs'].get('communication', 0),
            check_in = data['inputs'].get('check_in', 0),
            accuracy = data['inputs'].get('accuracy', 0),
            location = data['inputs'].get('location', 0),
            value = data.get('value', 0))
        Review(
            room_id = pk,
            reviewer_id = TOHOST,
            host_id = host,
            guest_id = user.id,
            rating = rating,
            content = data['inputs'].get('content', ' ')).save()
        return HttpResponse(status = 200)