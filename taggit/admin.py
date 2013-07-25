from django.contrib import admin
from django import forms
from taggit.models import Tag, TaggedItem, TagTransform
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

class TaggedItemInline(admin.StackedInline):
    model = TaggedItem
    extra = 0

class TagAdmin(admin.ModelAdmin):
    inlines = [
        TaggedItemInline
    ]
    ordering = ['name']
    search_fields = ['name']
    list_display = ['name', 'ad_alias']
    list_filter = ['ad_alias',]
    list_editable = ['ad_alias',]



class TagTransformAdminForm(forms.ModelForm):
    model = TagTransform

    def clean_rule(self, *args, **kwargs):
        """ Make sure this doesn't overlap with any other rule. """
        
        rule = self.cleaned_data.get('rule')
        tangled_rules = TagTransform.objects.filter(rule__iexact=rule).exclude(id=self.instance.id)
        if tangled_rules:
            error_msg = "There is already a <a href=\"{link}\">rule</a> to transform '{rule}.' You can't make a second.".format(
                rule = rule,
                link = reverse('admin:taggit_tagtransform_change', args=(tangled_rules[0].id,)),
                )
            raise forms.ValidationError(mark_safe(error_msg))
        return rule

    def clean_transform(self, *args, **kwargs):
        """ Make sure no existing rules apply the final output. """

        transform = self.cleaned_data.get('transform')
        tangled_rules = TagTransform.objects.filter(rule__iexact=transform)
        if transform and tangled_rules.count():
            if tangled_rules[0].transform:
                rule_msg = "converts '{}' to '{}'".format(transform, tangled_rules[0].transform)
            else:
                rule_msg = "removes '{}' from the list of tags".format(transform)
            error_msg = "Another <a href=\"{link}\">rule</a> {rule_msg}. \
                Transforming <i>to</i> that would cause strange problems.".format(
                    rule_msg = rule_msg,
                    link = reverse('admin:taggit_tagtransform_change', args=(tangled_rules[0].id,)),
                    )
            raise forms.ValidationError(mark_safe(error_msg))
        return transform


class TagTransformAdmin(admin.ModelAdmin):
    form = TagTransformAdminForm
    model = TagTransform
    order = ('rule',)
    search_fields = ('rule', 'transform',)

    list_per_page = 50
    list_display = ('type', 'rule', 'transform')


admin.site.register(Tag, TagAdmin)
admin.site.register(TagTransform, TagTransformAdmin)
