from telegram import Update
from telegram.ext import Updater, MessageHandler, CommandHandler, CallbackContext, Filters

import os
import json
import pprint
from bidict import bidict

pp = pprint.PrettyPrinter(indent=4)
db = bidict({})

def set_author_for_channel(author, channel_id):
    global db 

    print(author, channel_id)
    db[author] = channel_id
    save_db()
    print(db)

def handle_message(update: Update, context: CallbackContext) -> None:
    global db
    print(update)

    channel_id = update.channel_post.chat.id
    message_id = update.channel_post.message_id
    text = update.channel_post.text

    print("text", text)

    if "/set " in text:
        command = text
        author = command.replace("/set ", "")

        set_author_for_channel(author, channel_id)
    else:
        # handle any non set command
        pass

def save_db():
    global db

    with open('db.json', 'w') as db_file:
        db_file.write(json.dumps(dict(db)))

def read_db():
    global db

    try:
        with open('db.json', 'r') as db_file:
            raw_db = json.load(db_file)
            db = bidict(raw_db)
            print("INITIAL DB:\n{}\n"format(db))
    except:
        print("SOME READ ERROR ON DB")

def tg_listen():
    api_token = os.getenv('BUZZARD_TG_BOT_TOKEN')

    if api_token is None:
        raise Exception("BUZZARD_TG_BOT_TOKEN ENVIRONMENT VARIABLE IS NOT SET")

    updater = Updater(api_token)

    updater.dispatcher.add_handler(MessageHandler(Filters.all, handle_message))

    updater.start_polling()
    updater.idle()


# before doing anything get the DB setup
read_db()
setup_git()

# login to tg and begin to listen for updates in channels
tg_listen()

# handle exit condition
save_db()
