from .router import router
import logging
from services.ui.plugin_settings import create_plugin_setting, delete_plugin_setting_by_title
from schemas.plugin_setting import PluginSetting

logger = logging.getLogger("coffeebreak.activity-registration")

PLUGIN_TITLE = "Activities Registration"
PLUGIN_DESCRIPTION = "This plugin allows managing user registrations for activities with defined limits."

async def register_plugin():
    logger.debug("Activity registration plugin loaded.")

    setting = PluginSetting(
        title=PLUGIN_TITLE,
        description=PLUGIN_DESCRIPTION,
        inputs=[]
    )
    await create_plugin_setting(setting)

    return router

async def unregister_plugin():
    logger.debug("Activity registration plugin unloaded.")
    await delete_plugin_setting_by_title(PLUGIN_TITLE)

REGISTER = register_plugin
UNREGISTER = unregister_plugin

SETTINGS = {}
DESCRIPTION = PLUGIN_DESCRIPTION
