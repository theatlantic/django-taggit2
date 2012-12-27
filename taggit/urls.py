from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
	url(r'^static/(?P<path>.*)$', 'taggit.views.media', name='taggit-static'),
	url(r'^ajax$', 'taggit.views.ajax', name='taggit-ajax'),
	url(r'^generate-tags$', 'taggit.views.generate_tags', name='taggit-generate-tags'),
)
