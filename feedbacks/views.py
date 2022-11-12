from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .model_form import FeedbackModelForm
from .models import Feedback


@login_required
def feedbacks_view(request, *args, **kwargs):
    user = request.user
    if request.method == 'POST':
        form = FeedbackModelForm(user=user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thank you for your feedback!")
    else:
        form = FeedbackModelForm(user=user)
    context = {
        'feedbacks': Feedback.get_feedbacks_cache(),
        'form': form
    }
    return render(request, 'feedbacks/index.html', context, *args, **kwargs)
