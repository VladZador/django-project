from django.shortcuts import render

from .models import Item
from .forms import ItemForm


def items(request, *args, **kwargs):
    if request.method == "POST":
        form = ItemForm(request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
    else:
        form = ItemForm()
    context = {
        "items": Item.objects.all(),
        "form": form
    }
    return render(request, "items/index.html", context=context)
