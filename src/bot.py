import os
import json

import message_handler
from config import config, AUTHOR_DIR
from util.git import switch_branch

from telegram import Update
from telegram.ext import Updater, MessageHandler, CallbackContext, Filters

from bidict import bidict

class BuzzardBot():
    """
    This class runs the entire Bot. The main purpose is to start listening
    to Telegram messages and dispatch them to the correct module.

    Member Variables:
    db -- The DB mapping of author <-> channel
    """

    def __init__(self):
        """ Initializes the BuzzardBot. Sets up DB and Directories """
        self.db = self._read_db()
        self._setup_dirs()

    def start(self):
        """ Starts the BuzzardBot listening for Telegram updates  """
        updater = Updater(config.api_token)
        updater.dispatcher.add_handler(MessageHandler(Filters.all, handle_update))
        updater.start_polling()
        updater.idle()

    def stop(self):
        """ Stops the BuzzardBot listening for Telegram updates """
        # handle exit condition
        self.save_db()

    def _setup_dirs(self):
        """ Creates the proper directories in the Buzzard Git Repo """

        # create data/ directory if it doesn't exist
        data_dir = config.git_dir + "/consumption"
        if not os.path.exists(data_dir):
            os.mkdir(data_dir)

        for author, chan_id in self.db.items():
            if not os.path.exists(AUTHOR_DIR.format(author)):
                os.mkdir(AUTHOR_DIR.format(author))

    def _read_db(self):
        """ Opens the DB file and reads it into a member variable """
        db = bidict()

        # create .tg_bot dir if it doesn't exist
        if not os.path.exists(config.bot_dir):
            os.makedirs(config.bot_dir)

        # make sure we are on the right branch to load the db from
        switch_branch()
        try:
            with open(config.db_file, 'r') as db_file:
                raw_db = json.load(db_file)
                db = bidict(raw_db)
                print("INITIAL DB:\n{}\n".format(db))
        except:
            print("READ ERROR ON DB")
        
        return db

    def save_db(self):
        """ Writes the DB member variable out to a file """
        with open(config.db_file, 'w') as db_file:
            db_file.write(json.dumps(dict(self.db)))


def handle_update(update: Update, context: CallbackContext) -> None:
    """
    A wrapper to handle the update from Telegram. Just used to pass
    the instance of the bot to the Message Handler.

    Keyword Arguments:

    update -- The Telegram update
    context -- The callback context (see python_telegram_bot docs)
    """
    global bot

    # have the message handler dispatch the message
    message_handler.dispatch(bot, update)

# create the bot
bot = BuzzardBot()

# start the bot listening for Telegram messages
bot.start()
