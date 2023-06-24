import time

from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST, require_GET
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils import timezone
from django.http import Http404, HttpResponse

from asgiref.sync import sync_to_async

from notification.models import NotificationInfo

old_notifications = [[], []]


@require_GET
def notifications(request):
    notifications = NotificationInfo.objects.order_by('-date')
    old_notifications[0] = notifications
    return create_notifications(request, notifications)

@require_GET
def nav_notifications(request):
    notifications = NotificationInfo.objects.order_by('-date')
    old_notifications[1] = notifications
    return create_notifications(request, notifications, 3, 'notification/navbar_notifications.html')

@require_GET
@sync_to_async
def get_notifications(request):
    notifications = long_poll()

    if notifications is None:
        return HttpResponse(status=204)

    content = notifications
    return create_notifications(request, content)

@require_GET
@sync_to_async
def get_nav_notifications(request):
    notifications = long_poll(1)

    if notifications is None:
        return HttpResponse(status=204)
    
    content = notifications
    return create_notifications(request, content, 3, 'notification/navbar_notifications.html')

def long_poll(index=0):
    global old_notifications

    if old_notifications is None:
        old_notifications = [None, None]

    if old_notifications[index] is None:
        return None

    def check_notifications():
        global old_notifications
        notifications = NotificationInfo.objects.order_by('-date')
        if list(notifications) != list(old_notifications[index]):
            return notifications
        return None

    def long_poll_notifications():
        for _ in range(60):
            time.sleep(1)
            notifications = check_notifications()
            if notifications is not None:
                return notifications

        return None

    notifications = long_poll_notifications()

    if notifications is None:
        return None

    old_notifications[index] = notifications

    return notifications

def create_notifications(request, notifications, per_page=10, template='notification/notifications.html'):
    paginator = Paginator(notifications, per_page)
    page_number = request.GET.get('page')

    try:
        page_obj = paginator.get_page(page_number)
    except:
        raise Http404("Invalid page number")

    unread_str = ''

    unread_count = NotificationInfo.objects.filter(read=False).count()
    if unread_count > 99:
        unread_str = '99+'
    elif unread_count > 0:
        unread_str = str(unread_count)

    context = {'page_obj': page_obj, 'unread_count': unread_str}
    
    return render(request, template, context, status=200)

@require_POST
def add_notification(request):
    message = request.POST['message']
    type = request.POST['type']
    date = timezone.now()
    notification = NotificationInfo(message=message, type=type, date=date)
    notification.save()
    messages.success(request, 'Notification added.')
    return redirect('notification:notifications')


@require_POST
def delete_notification(request, id):
    notification = NotificationInfo.objects.get(id=id)
    notification.delete()
    messages.success(request, 'Notification deleted.')
    return redirect('notification:notifications')


@require_POST
def clear_notifications(request):
    NotificationInfo.objects.all().delete()
    messages.success(request, 'All notifications cleared.')
    return redirect('notification:notifications')


@require_POST
def toggle_read_notification(request, id):
    notification = NotificationInfo.objects.get(id=id)
    notification.read = not notification.read
    notification.save()
    messages.success(request, 'Notification read toggled.')
    return redirect('notification:notifications')

@require_POST
def read_notification(request, id):
    notification = NotificationInfo.objects.get(id=id)
    notification.read = True
    notification.save()
    messages.success(request, 'Notification read.')
    return redirect('notification:notifications')
