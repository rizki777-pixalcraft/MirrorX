import shutil, psutil
import signal
import pickle

from os import execl, path, remove
from sys import executable
import time

from telegram.ext import CommandHandler, run_async
from bot import dispatcher, updater, botStartTime
from bot.helper.ext_utils import fs_utils
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.message_utils import *
from .helper.ext_utils.bot_utils import get_readable_file_size, get_readable_time
from .helper.telegram_helper.filters import CustomFilters
from .modules import authorize, list, cancel_mirror, mirror_status, mirror, clone, watch, delete, speedtest, clone, 
from .modules import display_progress, help_Nekmo_ffmpeg, split_large_files, upload_to_tg, copy_similar_file

@run_async
def stats(update, context):
    currentTime = get_readable_time((time.time() - botStartTime))
    total, used, free = shutil.disk_usage('.')
    total = get_readable_file_size(total)
    used = get_readable_file_size(used)
    free = get_readable_file_size(free)
    sent = get_readable_file_size(psutil.net_io_counters().bytes_sent)
    recv = get_readable_file_size(psutil.net_io_counters().bytes_recv)
    cpuUsage = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    stats = f'<b>Bot Menyala Sejak ⌚:</b> {currentTime}\n' \
            f'<b>Sisa Penyimpanan🗄️:</b> {total}\n' \
            f'<b>Memory bot terpakai 🗃️:</b> {used}  ' \
            f'<b>Ruang Kosong Bot 🗃️:</b> {free}\n\n' \
            f'📇Pengunaan data bot📇\n<b>Uploaded :</b> {sent}\n' \
            f'<b>Yang lagi didownload:</b> {recv}\n\n' \
            f'<b>CPU 🖥️:</b> {cpuUsage}% ' \
            f'<b>RAM ⛏️:</b> {memory}% ' \
            f'<b>Disk 🗄️:</b> {disk}%'
    sendMessage(stats, context.bot, update)


@run_async
def start(update, context):
    start_Thisstring = f'''
    Iini bot bisa mirror link gd/mediafire/zippy/mega
Type /{BotCommands.HelpCommand} kalo pengen liat perintah bot
'''
    sendMessage(start_string, context.bot, update)


@run_async
def restart(update, context):
    restart_message = sendMessage("Bentar lagi restart", context.bot, update)
    # Save restart message object in order to reply to it after restarting
    fs_utils.clean_all()
    with open('restart.pickle', 'wb') as status:
        pickle.dump(restart_message, status)
    execl(executable, executable, "-m", "bot")


@run_async
def ping(update, context):
    start_time = int(round(time.time() * 1000))
    reply = sendMessage("Starting Ping", context.bot, update)
    end_time = int(round(time.time() * 1000))
    editMessage(f'{end_time - start_time} ms', reply)


@run_async
def log(update, context):
    sendLogFile(context.bot, update)


@run_async
def bot_help(update, context):
    help_string = f'''
/{BotCommands.HelpCommand}: Tutor botnya

/{BotCommands.MirrorCommand} [download_url][magnet_link]: Mulai Mirror bot dengan perintah /kaca (link mega/google drive/zippy/mediafire)

/{BotCommands.UnzipMirrorCommand} [download_url][magnet_link] : Sama kayak perintah mirror tapi bedanya ini langsung di ekstrak

/{BotCommands.TarMirrorCommand} [download_url][magnet_link]: Sama kayak perintah mirror tapi bedanya ini menjadikan file ekstensi .tar

/{BotCommands.WatchCommand} [youtube-dl supported link]: Nge download video dari youtube. Click /{BotCommands.WatchCommand} for more help.

/{BotCommands.TarWatchCommand} [youtube-dl supported link]: Sama kayak perintah watch tp bedanya ini diubah ke ekstensi .tar

/{BotCommands.CancelMirror} : Ngebatalin Mirror

/{BotCommands.StatusCommand}: Ngeliat status mirror

/{BotCommands.ListCommand} [search term]: Mencari list di google drive

/{BotCommands.StatsCommand}: Menampilkan system bot

/{BotCommands.AuthorizeCommand}: Supaya bot bisa digunain oleh orang lain/grup

/{BotCommands.LogCommand}: Log bot 

/{BotCommands.SpeedCommand} : Cek kecepatan internet

/{BotCommands.CloneCommand} : Clone link Google Drive

/{BotCommands.Upload_to_tgCommand} : Testing Commit, Upload ke Telegram
'''
    sendMessage(help_string, context.bot, update)


def main():
    fs_utils.start_cleanup()
    # Check if the bot is restarting
    if path.exists('restart.pickle'):
        with open('restart.pickle', 'rb') as status:
            restart_message = pickle.load(status)
        restart_message.edit_text("Restarted Successfully!")
        remove('restart.pickle')

    start_handler = CommandHandler(BotCommands.StartCommand, start,
                                   filters=CustomFilters.authorized_chat | CustomFilters.authorized_user)
    ping_handler = CommandHandler(BotCommands.PingCommand, ping,
                                  filters=CustomFilters.authorized_chat | CustomFilters.authorized_user)
    restart_handler = CommandHandler(BotCommands.RestartCommand, restart,
                                     filters=CustomFilters.owner_filter| CustomFilters.authorized_user)
    help_handler = CommandHandler(BotCommands.HelpCommand,
                                  bot_help, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user)
    stats_handler = CommandHandler(BotCommands.StatsCommand,
                                   stats, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user)
    log_handler = CommandHandler(BotCommands.LogCommand, log, filters=CustomFilters.owner_filter)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(ping_handler)
    dispatcher.add_handler(restart_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(stats_handler)
    dispatcher.add_handler(log_handler)
    updater.start_polling()
    LOGGER.info("Bot Started!")
    signal.signal(signal.SIGINT, fs_utils.exit_clean_up)


main()
