import inspect

# dir()
# >>> ['RuntimeException', 'String', 'TropoApp', 'TropoCall', 'TropoChoice', 'TropoEvent', '__name__', '_handleCallBack', '_parseTime', 'a', 'action', 'answer', 'appInstance', 'ask', 'call', 'callFactory', 'conference', 'conferenceFactory', 'context', 'createConference', 'currentApp', 'currentCall', 'destroyConference', 'engine', 'hangup', 'incomingCall', 'log', 'prompt', 'record', 'redirect', 'reject', 'say', 'startCallRecording', 'stopCallRecording', 'token', 'transcribe', 'transcription', 'transfer', 'wait']

if (currentCall):
    log("READ HERE: Incoming")
    
    # log(currentCall)   # object instance
    # log(action)        # undefined
    # log(incomingCall)  # Call instance
    # log(context)       # java context object
    
    # dir(currentCall)
    # >>> ['__doc__', '__init__', '__module__', '_call', 'answer', 'ask', 'calledID', 'calledName', 'callerID', 'callerName', 'channel', 'conference', 'getHeader', 'hangup', 'initialText', 'isActive', 'log', 'network', 'prompt', 'record', 'redirect', 'reject', 'say', 'startCallRecording', 'state', 'stopCallRecording', 'transfer', 'wait']
    
    # log(currentCall.calledID)       # 17738000911
    # log(currentCall.calledName)     # unknown
    # log(currentCall.callerID)       # 18057143797
    # log(currentCall.callerName)     # unknown
    # log(currentCall.channel)        # TEXT
    # log(inspect.getargspec(currentCall.getHeader))      # accepts [self, header_name]
    # log(currentCall.initialText)    # Test
    # log(currentCall.network)        # SMS
    # log(currentCall.state())          # RINGING
else:
    log("READ HERE: Outgoing")
    
    # log(currentCall)   # None
    # log(action)        # create
    # log(incomingCall)  # nullCall
    # log(context)       # java context object