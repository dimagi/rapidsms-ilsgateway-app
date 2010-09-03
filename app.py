#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from rapidsms.apps.base import AppBase

class App(AppBase):
    def start (self):
        """Configure your app in the start phase."""
        pass

    def parse (self, message):
        """Parse and annotate messages in the parse phase."""
        # stick a school on here, if we find it.  Otherwise 
        # just set the property empty
#        message.school = None
#        if message.reporter and message.reporter.location:
#            try:
#                message.school = School.objects.get(id=message.reporter.location.id)
#            except School.DoesNotExist:
#                pass
        pass

    def handle (self, message):
        """Add your main application logic in the handle phase."""
        pass

    def cleanup (self, message):
        """Perform any clean up after all handlers have run in the
           cleanup phase."""
        pass

    def outgoing (self, message):
        """Handle outgoing message notifications."""
        pass

    def stop (self):
        """Perform global app cleanup when the application is stopped."""
        pass