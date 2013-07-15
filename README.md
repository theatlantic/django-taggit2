django-taggit
=============

django-taggit2 is a fork of Alex Gaynor's [Django Taggit](https://github.com/alex/django-taggit)
that plugs into an automatic tagging function. We're using it with [TagSuggestor](https://github.com/theatlantic/tagsuggestor).

In Django settings, do this:

    TAGGIT_TAG_GENERATE_FUNC = 'my_utils_package.my_tagging_function'

This function should accept the admin forms context as a text block and return a list of tags.

-------

``django-taggit`` a simpler approach to tagging with Django.  Add ``"taggit"`` to your
``INSTALLED_APPS`` then just add a TaggableManager to your model and go::

    from django.db import models

    from taggit.managers import TaggableManager

    class Food(models.Model):
        # ... fields here

        tags = TaggableManager()


Then you can use the API like so::

    >>> apple = Food.objects.create(name="apple")
    >>> apple.tags.add("red", "green", "delicious")
    >>> apple.tags.all()
    [<Tag: red>, <Tag: green>, <Tag: delicious>]
    >>> apple.tags.remove("green")
    >>> apple.tags.all()
    [<Tag: red>, <Tag: delicious>]
    >>> Food.objects.filter(tags__name__in=["red"])
    [<Food: apple>, <Food: cherry>]

Tags will show up for you automatically in forms and the admin.

``django-taggit`` requires Django 1.1 or greater.

For more info checkout out the documentation.  And for questions about usage or
development you can contact the
`mailinglist <http://groups.google.com/group/django-taggit>`_.
