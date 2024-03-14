# context_processors.py
from .models import Notifications, CoordinatorFeedbacks

def unread_notifications(request):
    if request.user.is_authenticated:
        if hasattr(request.user, 'student'):
            student = request.user
            unread_notifications = Notifications.objects.filter(recipient=student, read=False).count()
            unread_feedbacks = CoordinatorFeedbacks.objects.filter(project__student=student, read=False).count()
            total_unread = unread_notifications + unread_feedbacks
        else:
            total_unread = 0
    else:
        total_unread = 0


    return {'total_unread': total_unread}