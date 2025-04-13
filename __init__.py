from .router import router
import logging

logger = logging.getLogger("coffeebreak.plugins.activity_registration")

def register_plugin():
    print("Activity registration plugin loaded.")

def unregister_plugin():
    print("Activity registration plugin unloaded.")

REGISTER = register_plugin
UNREGISTER = unregister_plugin
