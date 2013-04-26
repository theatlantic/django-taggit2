from django.contrib import admin

from taggit.models import Tag, TaggedItem, TagTransform


class TaggedItemInline(admin.StackedInline):
    model = TaggedItem
    extra = 0

class TagAdmin(admin.ModelAdmin):
    inlines = [
        TaggedItemInline
    ]
    ordering = ['name']
    search_fields = ['name']

class TagTransformAdmin(admin.ModelAdmin):
    model = TagTransform
    order = ('rule',)
    search_fields = ('rule', 'transform',)
    list_per_page = 50
    list_display = ('type', 'rule', 'transform')

admin.site.register(Tag, TagAdmin)
admin.site.register(TagTransform, TagTransformAdmin)
