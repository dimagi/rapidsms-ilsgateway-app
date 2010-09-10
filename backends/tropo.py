#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from rapidsms.backends.http import RapidHttpBacked

class TropoBackend(RapidHttpBacked):
    """ A RapidSMS backend for Tropo SMS API """

    def configure(self, config=None, **kwargs):
        self.config = config
        super(MyBackend, self).configure(**kwargs)

    def handle_request(self, request):
        self.debug('Request: %s' % request.POST)
        message = self.message(request.POST.get('session', ''))
        if message:
            self.route(message)
        return HttpResponse('OK')

    def message(self, data):
        
        sms = data.get('initialText', '')
        sender_dict = data.get('from', '')
        sender = sender_dict.get('id', '')
        if not sms or not sender:
            self.error('Missing from or text: %s' % data)
            return None
        now = datetime.datetime.utcnow()
        return super(MyBackend, self).message(sender, sms, now)

    def send(self, message):
        self.info('Sending message: %s' % message)
        data = {
            'From': self.config['number'],
            'To': message.connection.identity,
            'Body': message.text,
        }
        if 'callback' in self.config:
            data['StatusCallback'] = self.config['callback']
        self.debug('POST data: %s' % pprint.pformat(data))
        url = '/%s/Accounts/%s/SMS/Messages' % (self.api_version,
                                                self.config['account_sid'])
        try:
            response = self.account.request(url, 'POST', data)
        except Exception, e:
            self.exception(e.read())
            response = None
        if response:
            self.info('SENT')
            self.debug(response)