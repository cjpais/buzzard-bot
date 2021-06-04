import os
import json

from config import config, AUTHOR_DIR
from message_handler import handle_message

from telegram import Update
from telegram.ext import Updater, MessageHandler, CallbackContext, Filters

from bidict import bidict

class BuzzardBot():

    def __init__(self):
        self.db = self._read_db()
        self._setup_dirs()

    def start(self):
        updater = Updater(config.api_token)
        updater.dispatcher.add_handler(MessageHandler(Filters.all, dispatch_message))
        updater.start_polling()
        updater.idle()

    def stop(self):
        # handle exit condition
        self.save_db()

    def _setup_dirs(self):
        # create data/ directory if it doesn't exist
        data_dir = config.git_dir + "/consumption"
        if not os.path.exists(data_dir):
            os.mkdir(data_dir)

        for author, chan_id in self.db.items():
            if not os.path.exists(AUTHOR_DIR.format(author)):
                os.mkdir(AUTHOR_DIR.format(author))

    def _read_db(self):
        db = bidict()

        # create .tg_bot dir if it doesn't exist
        if not os.path.exists(config.bot_dir):
            os.makedirs(config.bot_dir)

        try:
            with open(config.db_file, 'r') as db_file:
                raw_db = json.load(db_file)
                db = bidict(raw_db)
                print("INITIAL DB:\n{}\n".format(db))
        except:
            print("READ ERROR ON DB")
        
        return db

    def save_db(self):
        with open(config.db_file, 'w') as db_file:
            db_file.write(json.dumps(dict(self.db)))


def dispatch_message(update: Update, context: CallbackContext) -> None:
    global bot
    handle_message(bot, update)

# create the bot
bot = BuzzardBot()

# start the bot listening for Telegram messages
bot.start()
