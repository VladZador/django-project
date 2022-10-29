from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from .models import Order


@shared_task
def delete_old_pending_orders():
    Order.objects.filter(
        is_active=True,
        created_at__lt=timezone.now() - timedelta(days=1)
    ).delete()
