from django.contrib import admin

from .models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("short_text", "user", "rating")
    list_filter = ("rating", )
    ordering = ("-updated_at",)

    def short_text(self, obj):
        return obj.text[:100]
