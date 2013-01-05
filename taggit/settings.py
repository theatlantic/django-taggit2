import os.path
from django.conf import settings
from django.core.urlresolvers import get_callable

TAGGIT_ROOT = os.path.normpath(os.path.dirname(__file__))
TAGGIT_MEDIA_DIR = getattr(settings, 'TAGGIT_MEDIA_DIR', os.path.join(TAGGIT_ROOT, 'media'))

TAGGIT_TAG_GENERATE_FUNC = getattr(settings, 'TAGGIT_TAG_GENERATE_FUNC', None)
if isinstance(TAGGIT_TAG_GENERATE_FUNC, basestring):
    TAGGIT_TAG_GENERATE_FUNC = get_callable(TAGGIT_TAG_GENERATE_FUNC)
