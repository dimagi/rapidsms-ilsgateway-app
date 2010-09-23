#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8


import sys

try:
    import settings # Assumed to be in the same directory.
except ImportError:
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r." % __file__)    
    sys.exit(1)

import csv
from os.path import dirname
from ilsgateway.models import ServiceDeliveryPoint

project_root = os.path.abspath(os.path.dirname(__file__))
in_file = os.path.join(project_root, "fixtures", "regions.cv")
model_name = "ServiceDeliveryPoint"

print "Loading facilities, districts and regions" % (in_file, out_file)

sdp = ServiceDeliveryPoint(name="ANewOne")
sdp.save()

#f = open(in_file, 'r' )
#reader = csv.reader( f )
#
#header_row = []
#entries = []

# debugging
# if model_name == 'app_airport.Airport':
#     import pdb ; pdb.set_trace( )

#for row in reader:
#    if not header_row:
#        header_row = row
#        continue
#        
#    pk = row[0]
#    model = model_name
#    fields = {}
#    for i in range(len(row)-1):
#        active_field = row[i+1]
#
#        # convert numeric strings into actual numbers by converting to either int or float
#        if active_field.isdigit():
#            try:
#                new_number = int(active_field)
#            except ValueError:
#                new_number = float(active_field)
#            fields[header_row[i+1]] = new_number
#        else:
#            fields[header_row[i+1]] = active_field.strip().lower()
#        
#    row_dict = {}
#    row_dict["pk"] = int(pk)
#    row_dict["model"] = model_name
#    
#    row_dict["fields"] = fields
#    entries.append(row_dict)
#
#fo.write("%s" % simplejson.dumps(entries, indent=4))
#
#f.close()
#fo.close()