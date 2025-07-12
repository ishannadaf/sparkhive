from .models import Notification

def notification_count(request):
    if request.user.is_authenticated:
        count = Notification.objects.filter(recipient=request.user, seen=False).count()
        return {'notification_count': count}
    return {}
