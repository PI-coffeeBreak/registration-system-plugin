from .router import router
import logging

logger = logging.getLogger("coffeebreak.activity-registration")

PLUGIN_TITLE = "registration-system-plugin"
NAME = "Registration System Plugin"
DESCRIPTION = "This plugin allows managing user registrations for activities with defined limits."

async def register_plugin():
    logger.debug("Activity registration plugin loaded.")
    return router

async def unregister_plugin():
    logger.debug("Activity registration plugin unloaded.")

REGISTER = register_plugin
UNREGISTER = unregister_plugin

CONFIG_PAGE = True
