# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding field 'Tag.ad_alias'
        db.add_column('taggit_tag', 'ad_alias', self.gf('django.db.models.fields.SlugField')(default='', max_length=50, db_index=True), keep_default=False)

        # Changing field 'TagTransform.transform'
        db.alter_column('taggit_tagtransform', 'transform', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True))
    
    
    def backwards(self, orm):
        
        # Deleting field 'Tag.ad_alias'
        db.delete_column('taggit_tag', 'ad_alias')

        # Changing field 'TagTransform.transform'
        db.alter_column('taggit_tagtransform', 'transform', self.gf('django.db.models.fields.CharField')(max_length=100))
    
    
    models = {
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'taggit.tag': {
            'Meta': {'object_name': 'Tag'},
            'ad_alias': ('django.db.models.fields.SlugField', [], {'default': "''", 'max_length': '50', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'})
        },
        'taggit.taggeditem': {
            'Meta': {'object_name': 'TaggedItem'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'taggit_taggeditem_tagged_items'", 'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'taggit_taggeditem_items'", 'to': "orm['taggit.Tag']"})
        },
        'taggit.tagtransform': {
            'Meta': {'object_name': 'TagTransform'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rule': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'transform': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'type': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'})
        }
    }
    
    complete_apps = ['taggit']
