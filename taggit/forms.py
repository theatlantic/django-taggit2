import os
from django import forms
from django.forms.util import flatatt
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from taggit.utils import parse_tags, edit_string_for_tags, clean_tag_string, transform_tags

class TagWidget(forms.TextInput):
    
    tag_suggest = None
    def __init__(self, generate_tags=None):
        super(TagWidget, self).__init__()
        self.generate_tags = generate_tags
        if generate_tags is not None:
            from taggit.settings import TAGGIT_TAG_GENERATE_FUNC
            if TAGGIT_TAG_GENERATE_FUNC is None:
                raise LookupError('TAGGIT_TAG_GENERATE_FUNC is not defined!')

    def get_media(self):
        """
        A method used to dynamically generate the media property,
        since we may not have the urls ready at the time of import,
        and then the reverse() call would fail.
        """
        from django.forms.widgets import Media as _Media
        from django.core.urlresolvers import NoReverseMatch, reverse
        media = super(TagWidget, self).media
        try:
            media_url = reverse('taggit-static', kwargs={'path': ''})
        except NoReverseMatch:
            # Nothing to add
            pass
        else:
            media.add_js([os.path.join(media_url, 'js', 'tagit.js'),
                          os.path.join(media_url, 'js', 'taggit.js')
            ])
            media.add_css({'all': (
                os.path.join(media_url, 'css', 'tagit-dark-grey.css'),
            )})
        return media
    
    media = property(get_media)
    
    def render_values(self, tags, attrs):
        builder = []
        builder.append(u'<ul%s>' % flatatt(attrs))
        for tag_name in tags:
            tag_attr = {'tagValue': tag_name, 'value': tag_name}
            builder.append(u'<li%s>%s</li>' % (flatatt(tag_attr), tag_name))
        builder.append(u'</ul>')
        return ''.join(builder)
    
    def default_render(self, name, value, attrs):
        # Get the initial rendered box
        raw_value = value
        if value is not None and not isinstance(value, basestring):
            value = edit_string_for_tags(value)
        return super(TagWidget, self).render(name, value, attrs)

    def render(self, name, value, attrs=None):
        if attrs is None:
            attrs = {}

        # Get the original input field, which we will hide on render
        attrs.update({'class': 'taggit-tags'})
        rendered = self.default_render(name, value, attrs)

        if self.generate_tags is not None:
            attrs.update({'data-tag-content-field': self.generate_tags});

        # We need to get rid of the id if it's in attrs
        if 'id' in attrs:
            attrs['data-field-id' ] = attrs.pop('id')

        tag_list = self.render_values(value or [], attrs)
        if self.generate_tags is not None:
            attrs = flatatt({'data-field': name,
                             'class':'taggit-tag-suggest',
                             'type': 'button'})
            tag_list += u"<button%s>Generate</button>" % attrs

        return mark_safe(rendered + tag_list)

    def _has_changed(self, initial, data):
        """
        Whether the input value has changed. Used for recording in
        django_admin_log.
        
        Because initial is passed as a queryset, and data is a string,
        we need to turn the former into a string and run the latter
        through a function which cleans it up and sorts the tags in it.
        """
        if initial is None:
            initial = ""
        elif hasattr(initial, 'select_related'):
            initial_vals = [o.tag for o in initial.select_related("tag")]
            initial = edit_string_for_tags(initial_vals)
        else:
            try:
                if not initial:
                    initial = ""
                else:
                    initial = edit_string_for_tags(initial)
            except TypeError, ValueError:
                initial = ""
        data = clean_tag_string(data)
        return super(TagWidget, self)._has_changed(initial, data)


class TagField(forms.CharField):
    widget = TagWidget

    def __init__(self, *args, **kwargs):
        self.transform_on_save  = kwargs.pop('transform_on_save', False)
        super(TagField, self).__init__(*args, **kwargs)

    def clean(self, value):
        value = super(TagField, self).clean(value)
        try:
            tags = parse_tags(value)
            if self.transform_on_save:
                tags = transform_tags(tags, delete_tags=False)
            return tags
        except ValueError:
            raise forms.ValidationError(_("Please provide a comma-separated list of tags."))

    def prepare_value(self, value):

        if isinstance(value,  basestring):
            try:
                value = parse_tags(value)
            except ValueError:
                raise forms.ValidationError(_("Please provide a comma-separated list of tags."))
        else:
            value = [unicode(item.tag) for item in value]

        return super(TagField, self).prepare_value(value)
