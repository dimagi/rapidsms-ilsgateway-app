from rapidsms.contrib.handlers.handlers.keyword import KeywordHandler

class Help(KeywordHandler):
    """
    """

    keyword = "help"

    def help(self):
        try:
            self.msg.contact.contactdetail
            self.respond('Welcome to ILSGateway. Available commands are soh, delivered, not delivered, submitted, not submitted')
        except:
            self.respond("To register, send register <name> <msd code>. example: register john patel d34002")
