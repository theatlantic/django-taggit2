from itertools import count

from django.db.models import Q
from django.utils.encoding import force_unicode
from django.utils.functional import wraps

from taggit.models import TagTransform


def parse_tags(tagstring):
    """
    Parses tag input, with multiple word input being activated and
    delineated by commas and double quotes. Quotes take precedence, so
    they may contain commas.

    Returns a sorted list of unique tag names.

    Ported from Jonathan Buchanan's `django-tagging
    <http://django-tagging.googlecode.com/>`_
    """
    if not tagstring:
        return []

    tagstring = force_unicode(tagstring)

    # Special case - if there are no commas or double quotes in the
    # input, we don't *do* a recall... I mean, we know we only need to
    # split on spaces.
    if u',' not in tagstring and u'"' not in tagstring:
        words = list(set(split_strip(tagstring, u' ')))
        words.sort()
        return words

    words = []
    buffer = []
    # Defer splitting of non-quoted sections until we know if there are
    # any unquoted commas.
    to_be_split = []
    saw_loose_comma = False
    open_quote = False
    i = iter(tagstring)
    try:
        while True:
            c = i.next()
            if c == u'"':
                if buffer:
                    to_be_split.append(u''.join(buffer))
                    buffer = []
                # Find the matching quote
                open_quote = True
                c = i.next()
                while c != u'"':
                    buffer.append(c)
                    c = i.next()
                if buffer:
                    word = u''.join(buffer).strip()
                    if word:
                        words.append(word)
                    buffer = []
                open_quote = False
            else:
                if not saw_loose_comma and c == u',':
                    saw_loose_comma = True
                buffer.append(c)
    except StopIteration:
        # If we were parsing an open quote which was never closed treat
        # the buffer as unquoted.
        if buffer:
            if open_quote and u',' in buffer:
                saw_loose_comma = True
            to_be_split.append(u''.join(buffer))
    if to_be_split:
        if saw_loose_comma:
            delimiter = u','
        else:
            delimiter = u' '
        for chunk in to_be_split:
            words.extend(split_strip(chunk, delimiter))
    words = list(set(words))
    words.sort()
    return words


def split_strip(string, delimiter=u','):
    """
    Splits ``string`` on ``delimiter``, stripping each resulting string
    and returning a list of non-empty strings.

    Ported from Jonathan Buchanan's `django-tagging
    <http://django-tagging.googlecode.com/>`_
    """
    if not string:
        return []

    words = [w.strip() for w in string.split(delimiter)]
    return [w for w in words if w]


def edit_string_for_tags(tags):
    """
    Given list of ``Tag`` instances or tag strings, creates a string
    representation of the list suitable for editing by the user, such
    that submitting the given string representation back without
    changing it will give the same list of tags.

    Tag names which contain commas will be double quoted.

    If any tag name which isn't being quoted contains whitespace, the
    resulting string of tag names will be comma-delimited, otherwise
    it will be space-delimited.

    Ported from Jonathan Buchanan's `django-tagging
    <http://django-tagging.googlecode.com/>`_
    """
    names = []
    for tag in tags:
        if hasattr(tag, 'name'):
            name = tag.name
        elif isinstance(tag, (str, unicode,)):
            name = tag
        else:
            continue
        if u',' in name or u' ' in name:
            names.append('"%s"' % name)
        else:
            names.append(name)
    return u', '.join(sorted(names))

def clean_tag_string(tag_string):
    tags = parse_tags(tag_string)
    return edit_string_for_tags(tags)
	
def require_instance_manager(func):
    @wraps(func)
    def inner(self, *args, **kwargs):
        if self.instance is None:
            raise TypeError("Can't call %s with a non-instance manager" % func.__name__)
        return func(self, *args, **kwargs)
    return inner

def tags_to_word_idx(tags):
    word_idxs = {}
    for i, tag in enumerate(tags):
        for word in tag.split():
            try:
                word_idxs[word].append(i)
            except KeyError:
                word_idx = word_idxs[word] = [i]

    return word_idxs

def word_idx_to_tags(word_idxs, tags):
    r_word_idx = dict((idx, word) for word, idx in word_idxs.iteritems())
    new_tags = []
    for tag in tags:
        new_tag = []
        for idx in tag:
            word = r_word_idx[idx]
            # Formatting tweak: if it's all lower case, capitalize it.
            # Otherwise, let it be
            if word is not None and word.isalpha() and word.islower():
                word = word.capitalize()

            new_tag.append(word)
        # words that are set to None indicate we want to delete the entire tag

        if None not in new_tag:
            new_tags.append(u' '.join(new_tag))

    return new_tags

def apply_delete_tags(tags):
    # Find tags that we intend to completely delete
    to_delete = set(t.rule for t in TagTransform.objects.filter(type=0, transform='', rule__in=tags))
    return [t for t in tags if t not in to_delete]

def substitute_tags(tags):
    tags = tags[:]
    # Get normal word transforms
    transforms = TagTransform.objects.filter(type=0, rule__in=tags).exclude(transform="")
    transform_map = dict((t.rule, t) for t in transforms)
    for i, tag in enumerate(tags):
        if tag in transform_map:
            tags[i] = transform_map[tag].apply_transform(tag)

    return tags

def capitalize_tag(tag):
    return u' '.join(word.capitalize() for word in tag.split())

def substitute_words_in_tags(tags, delete_tags=True):

    if not tags: # Nothing to transform
        return tags
    
    # Break apart tags into their constituent words
    word_idxs = tags_to_word_idx(tags)

    # Figure out how words are to be transformed and transform them
    q = reduce(lambda x, y: x | y, (Q(rule__icontains=word) for word in word_idxs))
    q = Q(type=1) & q
    transforms = TagTransform.objects.filter(q)
    if not delete_tags:
        transforms = transforms.exclude(transform="")

    # Loop over each transform, attempting to figure out if a rule applies
    # If two different rules would apply to the same transform, we don't
    # know how to intelligently handle that, so don't apply _any_ transform
    new_tags = tags[:]
    seen = set()
    for transform in transforms:
        cur_seen = set() 
        for word in transform.rule.split():
            idxs = word_idxs.get(word, ())
            for idx in idxs:
                # Have we already transformed this?
                if idx in seen and not cur_seen:
                    # Yep, mulligan on the transform
                    new_tags[idx] = tags[idx]

                # Have we transformed it already this round?
                if idx in cur_seen:
                    continue

                old_tag = tags[idx]
                new_tag = transform.apply_transform(old_tag)
                if old_tag != new_tag: 
                    # Transform was applied!
                    cur_seen.add(idx)
                    new_tags[idx] = new_tag

        seen |= cur_seen

    return new_tags

def transform_tags(original_tags, delete_tags=True):
    # We want the lowercase version for all matching
    tags = map(unicode.lower, original_tags)

    if delete_tags:
        tags = apply_delete_tags(tags)

    # Substitute complete tags
    tags = substitute_tags(tags)

    # Substitute sub words
    tags = substitute_words_in_tags(tags, delete_tags)
    cap_tags = sorted(set(capitalize_tag(t) for t in tags))
    return list(cap_tags)
