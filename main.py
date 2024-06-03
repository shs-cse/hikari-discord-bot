import sys, warnings, miru
import hikari, crescent
from bot_variables import state
from bot_variables.config import FileName, InfoField
from wrappers.utils import FormatText
from setup_validation.json_inputs import check_and_load_info


def main():
    # check if `-d` flag was used `python -dO main.py`
    state.is_debug = 'd' in sys.orig_argv[1]
    warnings.simplefilter("ignore") # ignore pygsheets warnings
    # validate and update state.info
    check_and_load_info()
    # hikari + crescent -> create bot and client 
    bot = hikari.GatewayBot(state.info[InfoField.BOT_TOKEN], 
                            intents=hikari.Intents.ALL,
                            logs="INFO" if state.is_debug else "WARNING")
    this_guild_id = int(state.info[InfoField.GUILD_ID])
    client = crescent.Client(bot,
                             default_guild=this_guild_id)
    # load commands and pluins
    client.plugins.load_folder(FileName.COMMANDS_FOLDER)
    if not state.is_debug:
        client.plugins.unload("bot_commands.bulk_delete")
    # client.plugins.load("sync.init")
    client.plugins.load("setup_validation.discord_sec")
    client.plugins.load("wrappers.discord")
    # initialize miru
    state.miru_client = miru.Client(bot)
    # run the bot
    bot.run(
        # enable asyncio debug to detect blocking and slow code.
        asyncio_debug=state.is_debug,
        # enable coroutine tracking, makes some asyncio errors clearer.
        coroutine_tracking_depth=20 if state.is_debug else None, 
        # initial discord status of the bot
        status=hikari.Status.IDLE)

if __name__ == "__main__":
    main()