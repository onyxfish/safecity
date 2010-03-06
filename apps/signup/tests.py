from rapidsms.tests.scripted import TestScript
from app import App

class TestApp (TestScript):
    apps = (App,)

    testRegister = """
      8005555555 > on
      8005555555 < Please provide your location.
      8005555555 > on Austin & Augusta
      8005555555 < Thank you for registering.
      8005555555 > on Laramie & Augusta
      8005555555 < Your informatin has been updated.
      8005555555 > update Austin & Augusta
      8005555555 < Your information has been updated.
      8005555555 > off
      8005555555 < Your number has been unregistered.
      8005555555 > off
      8005555555 < Your number has been unregistered.
      8005555555 > on
      8005555555 < Thank you for registering.
    """