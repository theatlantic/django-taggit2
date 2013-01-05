(function($) {
    
    var taggitPrefix = '/';
    
    var scripts = document.getElementsByTagName('SCRIPT');
    for (var i = 0,l=scripts.length; i < l; i++) {
        var src = scripts[i].getAttribute('src');
        if (typeof src == 'string' && src.length) {
            var matches = src.match(/^(.+\/)static\/js\/taggit\.js/);
            if (matches) {
                taggitPrefix = matches[1];
            }
        }
    }
    
    function split(val) {
        return val.split(/,\s*/);
    }
    
    function extractLast(term) {
        return split(term).pop();
    }
    
    function setup_autocomplete() {
        $.getJSON(taggitPrefix + 'ajax', {}, function(data) {
            var availableTags = data.map(function(i) {
                return i.fields.name;
            });
            if ($.ui && $.ui.autocomplete && $.ui.autocomplete.filter) {
                $('.taggit-tags')
                // don't navigate away from the field on tab when selecting an item
                .bind("keydown", function(event) {
                    if (event.keyCode === $.ui.keyCode.TAB &&
                            $(this).data("autocomplete").menu.active) {
                        event.preventDefault();
                    }
                })
                .autocomplete({
                    minLength: 2,
                    source: function(request, response) {
                        // delegate back to autocomplete, but extract the last term
                        response($.ui.autocomplete.filter(
                            availableTags, extractLast(request.term)));
                    },
                    focus: function() {
                        // prevent value inserted on focus
                        return false;
                    },
                    select: function(event, ui) {
                        var terms = split(this.value);
                        // remove the current input
                        terms[terms.length-1] = ui.item.value;
                        // add placeholder to get the comma-and-space at the end
                        terms.push("");
                        this.value = terms.join(", ");
                        return false;
                    }
                });                
            } else {
                $('.taggit-tags').autocomplete({
                    source: availableTags
                });
            }

        });
    }

    function get_contents_by_name(context, field_name) {
        var $form = $(context).parents('form').slice(0,1);
        var $field = $form.find('[name='+field_name +']');

        // Explicit check to CKEDITOR
        if($field[0].tagName === 'TEXTAREA' && 
               window.CKEDITOR !== undefined && 
               CKEDITOR.instances[$field.attr('id')] !== undefined) {
            return CKEDITOR.instances[$field.attr('id')].getData();
        }
        return $field.val();
    }

    function setup_generate_tags() {
        var selector = 'button.taggit-tag-suggest';
        $(selector).live('click', function() {
            // Get content field to use and url to query
            var $input = $(this).prev(),
                query_url = taggitPrefix + 'generate-tags',
                content_field = $input.attr('data-tag-content-field'),
                self = this;
                
            var raw_contents = content_field.split(',').map(function(cf) {
                return get_contents_by_name(self, cf); 
            }).join('\n');
            
            var prev = $(document.body).css('cursor');
            $(document.body).css('cursor', 'wait');

            $.ajax({
                url: query_url,
                type: 'POST',
                dataType: 'jsonp',
                data: {'contents': raw_contents},
                success: function(new_tags) {
                    // Make sure to dedup the provided tags against the
                    // already given tags, normalizing as best we can.
                    var tags = split( $input.val() );
                    for(var set = {}, i = 0; i < tags.length; i++) {
                        var tag = tags[i].toLowerCase();
                        if(!/^".+"$/.test(tag)) {
                            tag = '"' + tag + '"';
                        }
                        console.log("Existing tag: " + tag);
                        set[tag] = true;
                    }

                    // Filter out tags that already exist
                    tags.push.apply(tags, new_tags.map(function(t) {
                        return '"'+t+'"';
                    }).filter(function(i){ 
                        return set[i.toLowerCase()]  === undefined ;
                    }));
                    console.log('New tag set:' + tags.join(','));
                    $input.val(tags.join(', '));
                    $(document.body).css('cursor',prev);
                },
                failure: function() {
                    $(document.body).css('cursor',prev);
                }
                
            });

        });
    }

    $(document).ready(function() {
        setup_autocomplete();
        setup_generate_tags();
    });

})((typeof window.django != 'undefined') ? django.jQuery : jQuery);
