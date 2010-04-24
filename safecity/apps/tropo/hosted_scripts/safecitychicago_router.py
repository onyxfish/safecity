from urllib import urlencode
from urllib2 import urlopen

if (currentCall):
    log('Incoming call from %s' % currentCall.callerID)
    
    params = {
        'sender': '+' + currentCall.callerID,
        'text': currentCall.initialText,
        'channel': currentCall.channel,
        'network': currentCall.network,
    }
    
    urlopen('http://dev.safecitychicago.org/tropo/incoming/', urlencode(params))
else:
    log('Outgoing call to %s' % recipients)
    
    recipients = recipients.split(',')
    
    for recipient in recipients:
        log(recipient)
        call('tel:' + recipient, { 'channel': 'TEXT', 'network': 'SMS' })
        say(text)
        hangup()