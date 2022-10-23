from django.utils.safestring import mark_safe


class ThumbnailAdminMixin:
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if isinstance(readonly_fields, list):
            readonly_fields.append('image_field')
        elif isinstance(readonly_fields, tuple):
            readonly_fields = readonly_fields + ('image_field',)
        return readonly_fields

    def get_list_display(self, request):
        list_display = super().get_list_display(request)
        if isinstance(list_display, list):
            list_display.insert(0, 'image_field')
        elif isinstance(list_display, tuple):
            list_display = ('image_field',) + list_display
        return list_display

    @mark_safe
    def image_field(self, obj):
        if not obj.image:
            return 'No image'
        return f'<img src="{obj.image.url}" width="64" height="64"/>'

    # def image_field(self, obj):
    #     return mark_safe(f"<img src='{obj.image.url}' "
    #                      f"width='64' height='64'/>")

    image_field.short_description = 'Image thumbnail'

    class Meta:
        abstract = True
