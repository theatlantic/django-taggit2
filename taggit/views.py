from django.views.decorators.http import require_POST
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.views.generic.list_detail import object_list
from django.core import serializers
from django.utils import simplejson
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from taggit.models import TaggedItem, Tag
import utils

def ajax(request):
    ''' get all of the tags available and return as a json array'''
    data = serializers.serialize('json', Tag.objects.order_by('slug').all(),
        fields=('name'), ensure_ascii=False)
    return HttpResponse(data)

def tagged_object_list(request, slug, queryset, **kwargs):
    if callable(queryset):
        queryset = queryset()
    tag = get_object_or_404(Tag, slug=slug)
    qs = queryset.filter(pk__in=TaggedItem.objects.filter(
        tag=tag, content_type=ContentType.objects.get_for_model(queryset.model)
    ).values_list("object_id", flat=True))
    if "extra_context" not in kwargs:
        kwargs["extra_context"] = {}
    kwargs["extra_context"]["tag"] = tag
    return object_list(request, qs, **kwargs)

def media(request, path):
    from django.views.static import serve
    from taggit.settings import TAGGIT_MEDIA_DIR
    return serve(request, path, TAGGIT_MEDIA_DIR)

@csrf_exempt
@require_POST
def generate_tags(request):
    if 'contents' not in request.POST or 'callback' not in request.POST:
        return HttpResponse(status=501)
    from taggit.settings import TAGGIT_TAG_GENERATE_FUNC
    if TAGGIT_TAG_GENERATE_FUNC is None:
        return HttpResponse(status=501)

    # Generate tags from the content
    content = request.POST['contents']
    tags = TAGGIT_TAG_GENERATE_FUNC(content)

    # Filter out tags that are in our 'bad' list
    # stub
    tags = utils.filter_tags(tags)
    data = simplejson.dumps(tags)
    return HttpResponse(u'%s(%s)' % (request.POST['callback'], data),
                        content_type='application/json')
