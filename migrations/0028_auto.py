# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Removing M2M table for field child_node_types on 'NodeType'
        db.delete_table('ilsgateway_nodetype_child_node_types')

        # Removing M2M table for field child_node on 'Node'
        db.delete_table('ilsgateway_node_child_node')


    def backwards(self, orm):
        
        # Adding M2M table for field child_node_types on 'NodeType'
        db.create_table('ilsgateway_nodetype_child_node_types', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_nodetype', models.ForeignKey(orm['ilsgateway.nodetype'], null=False)),
            ('to_nodetype', models.ForeignKey(orm['ilsgateway.nodetype'], null=False))
        ))
        db.create_unique('ilsgateway_nodetype_child_node_types', ['from_nodetype_id', 'to_nodetype_id'])

        # Adding M2M table for field child_node on 'Node'
        db.create_table('ilsgateway_node_child_node', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_node', models.ForeignKey(orm['ilsgateway.node'], null=False)),
            ('to_node', models.ForeignKey(orm['ilsgateway.node'], null=False))
        ))
        db.create_unique('ilsgateway_node_child_node', ['from_node_id', 'to_node_id'])


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'ilsgateway.contactdetail': {
            'Meta': {'object_name': 'ContactDetail'},
            'contact': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['rapidsms.Contact']", 'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ilsgateway.Node']", 'null': 'True'}),
            'primary': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ilsgateway.ContactRole']", 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        'ilsgateway.contactrole': {
            'Meta': {'object_name': 'ContactRole'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        'ilsgateway.node': {
            'Meta': {'object_name': 'Node'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'node_location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ilsgateway.NodeLocation']", 'null': 'True', 'blank': 'True'}),
            'node_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ilsgateway.NodeType']", 'null': 'True', 'blank': 'True'}),
            'products': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['ilsgateway.Product']", 'through': "orm['ilsgateway.NodeProductReport']", 'symmetrical': 'False'})
        },
        'ilsgateway.nodelocation': {
            'Meta': {'object_name': 'NodeLocation'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'parent_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'point': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['locations.Point']", 'null': 'True', 'blank': 'True'})
        },
        'ilsgateway.nodeproductreport': {
            'Meta': {'ordering': "('-report_date',)", 'object_name': 'NodeProductReport'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ilsgateway.Node']"}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ilsgateway.Product']"}),
            'quantity': ('django.db.models.fields.IntegerField', [], {}),
            'report_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2010, 9, 1, 11, 35, 27, 569000)', 'auto_now_add': 'True', 'blank': 'True'}),
            'report_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ilsgateway.ProductReportType']"})
        },
        'ilsgateway.nodestatus': {
            'Meta': {'ordering': "('-status_date',)", 'object_name': 'NodeStatus'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ilsgateway.Node']"}),
            'status_date': ('django.db.models.fields.DateTimeField', [], {}),
            'status_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ilsgateway.NodeStatusType']"})
        },
        'ilsgateway.nodestatustype': {
            'Meta': {'object_name': 'NodeStatusType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'ilsgateway.nodetype': {
            'Meta': {'object_name': 'NodeType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        'ilsgateway.product': {
            'Meta': {'object_name': 'Product'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'product_code': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'sms_code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'units': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'ilsgateway.productreporttype': {
            'Meta': {'object_name': 'ProductReportType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'sms_code': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'locations.point': {
            'Meta': {'object_name': 'Point'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.DecimalField', [], {'max_digits': '13', 'decimal_places': '10'}),
            'longitude': ('django.db.models.fields.DecimalField', [], {'max_digits': '13', 'decimal_places': '10'})
        },
        'rapidsms.contact': {
            'Meta': {'object_name': 'Contact'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '6', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        }
    }

    complete_apps = ['ilsgateway']
