from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST, require_GET
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils import timezone
from django.http import Http404

from notification.models import NotificationInfo


@require_GET
def notifications(request):
    notifications = NotificationInfo.objects.order_by('-date')

    paginator = Paginator(notifications, 10)
    page_number = request.GET.get('page')

    try:
        page_obj = paginator.get_page(page_number)
    except:
        raise Http404("Invalid page number")

    context = {'page_obj': page_obj}
    return render(request, 'notification/notifications.html', context)


@require_POST
def add_notification(request):
    message = request.POST['message']
    type = request.POST['type']
    date = timezone.now()
    notification = NotificationInfo(message=message, type=type, date=date)
    notification.save()
    messages.success(request, 'Notification added.')
    return redirect('notifications')


@require_POST
def delete_notification(request, id):
    notification = NotificationInfo.objects.get(id=id)
    notification.delete()
    messages.success(request, 'Notification deleted.')
    return redirect('notifications')


@require_POST
def clear_notifications(request):
    NotificationInfo.objects.all().delete()
    messages.success(request, 'All notifications cleared.')
    return redirect('notifications')


@require_POST
def toggle_read_notification(request, id):
    notification = NotificationInfo.objects.get(id=id)
    notification.read = not notification.read
    notification.save()
    messages.success(request, 'Notification read toggled.')
    return redirect('notifications')
