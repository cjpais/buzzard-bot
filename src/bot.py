import re
import os
import sys
import json
import pprint

from telegram import Update, Bot
from telegram.ext import Updater, MessageHandler, CommandHandler, CallbackContext, Filters
from jinja2 import Environment, FileSystemLoader

from pytz import timezone
from bidict import bidict
from lxml.html import parse
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.request import urlopen

templateLoader = FileSystemLoader(searchpath="../templates")
env = Environment(loader=templateLoader)

BUZZARD_GIT_DIR = "../BUZZARD"
BUZZARD_BOT_DIR = BUZZARD_GIT_DIR + "/.tg_bot"
DB_FILE = BUZZARD_BOT_DIR + "/db.json"
AUTHOR_DIR = BUZZARD_GIT_DIR + "/consumption/{}"

pp = pprint.PrettyPrinter(indent=4)
db = bidict({})

PT = timezone("America/Los_Angeles")

def url_valid(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return re.match(regex, url) is not None

def get_url_title(url):
    title = ""

    if url_valid(url):
        page = urlopen(url)
        p = parse(page)

        try:
            title = p.find(".//title").text 
        except:
            print("error getting title from url", url)
    else:
        # take the first 50 characters and call it the title
        title = url[:50]
        
    return title

def add_all_to_git(msg):
    global branch

    wd = os.getcwd()
    os.chdir(BUZZARD_GIT_DIR)
    os.system("git checkout {}".format(branch))
    os.system("git pull origin {}".format(branch))
    os.system("git add consumption/*")
    os.system("git add .tg_bot/*")
    os.system('git commit -m "{}"'.format(msg))
    os.system("git push origin {}".format(branch))
    os.chdir(wd)

def set_author_for_channel(author, channel_id):
    global db 

    bot = Bot(api_token)
    author_doesnt_exist = db.get(author) is None
    channel_doesnt_exist = db.inverse.get(channel_id) is None

    if author_doesnt_exist and channel_doesnt_exist:
        db[author] = channel_id
        save_db()
        add_author_to_git(author)
        bot.sendMessage(channel_id, "Author {} Successfully Added".format(author))

        add_all_to_git("Author {} added for channel {}".format(author, channel_id))
    elif not author_doesnt_exist and not channel_doesnt_exist:
        bot.sendMessage(channel_id, "Author {} and Channel {} already added".format(author, channel_id))
    elif not author_doesnt_exist:
        bot.sendMessage(channel_id, "Author {} already added in a different channel ({})".format(author, db.get(author)))
    elif not channel_doesnt_exist:
        bot.sendMessage(channel_id, "Channel {} already added for a different author ({})".format(channel_id, db.inverse.get(channel_id)))

def handle_message(update: Update, context: CallbackContext) -> None:
    global db
    print(update)

    channel_id = update.channel_post.chat.id
    message_id = update.channel_post.message_id
    message = update.channel_post.text
    date = update.channel_post.date.astimezone(PT)
    date_string = date.strftime("%x - %-I:%M%p")

    try:
        reply_id = update.channel_post.reply_to_message.message_id
    except AttributeError:
        reply_id = None

    print("message", message)

    if "/set " in message:
        command = message
        author = command.replace("/set ", "")

        set_author_for_channel(author, channel_id)
    elif "/remove " in message:
        pass
    else:
        title = ""
        author = db.inverse[channel_id]
        author_dir = AUTHOR_DIR.format(author)

        if reply_id:
            # find existing file and append to it instead of creating new file
            dir_files = os.listdir(author_dir)

            print("replyid", reply_id)

            fn = None
            for df in dir_files:
                file_id = int(df.split("_")[-1].replace('.md', ''))

                if file_id == reply_id:
                    fn = "{}/{}".format(author_dir, df)
                    break
            
            if not fn:
                raise Exception("Could not find message {} for author {}".format(reply_id, author))
            
            f = open(fn, 'a')
            f.write("\n\n_[{}]:_\n\n{}".format(date_string, message))
        else:
            #title = get_url_title(message).replace(" ", "_")
            fn = "{}/{}_{}.md".format(author_dir, title[:150], message_id)
            f = open(fn, 'w')

            template = env.get_template("tg-post.md")

            data = template.render(author=author, 
                    content=message)
                    #content=message,
                    #date=date_string)
            f.write(data)

        f.close()
        
        add_all_to_git("added {} from {}".format(message, author))

def save_db():
    global db

    with open(DB_FILE, 'w') as db_file:
        db_file.write(json.dumps(dict(db)))

def read_db():
    global db

    # create .tg_bot dir if it doesn't exist
    if not os.path.exists(BUZZARD_BOT_DIR):
        os.makedirs(BUZZARD_BOT_DIR)

    try:
        with open(DB_FILE, 'r') as db_file:
            raw_db = json.load(db_file)
            db = bidict(raw_db)
            print("INITIAL DB:\n{}\n".format(db))
    except:
        print("SOME READ ERROR ON DB")

def tg_listen():

    updater = Updater(api_token)

    updater.dispatcher.add_handler(MessageHandler(Filters.all, handle_message))

    updater.start_polling()
    updater.idle()

def add_author_to_git(author):
    author_dir = AUTHOR_DIR.format(author)
    if not os.path.exists(author_dir):
        os.mkdir(author_dir)

def setup_dirs():
    global db

    # create data/ directory if it doesn't exist
    data_dir = BUZZARD_GIT_DIR + "/consumption"
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)

    for author, chan_id in db.items():
        if not os.path.exists(AUTHOR_DIR.format(author)):
            os.mkdir(AUTHOR_DIR.format(author))


# make sure we have an API token for the bot
api_token = os.getenv('BUZZARD_TG_BOT_TOKEN')
if api_token is None:
    raise Exception("BUZZARD_TG_BOT_TOKEN ENVIRONMENT VARIABLE IS NOT SET")

branch = "main"
if len(sys.argv) == 2:
    if sys.argv[1] == "test" or sys.argv[1] == "main":
        branch = sys.argv[1]
    else:
        raise Exception("INCORRECT BRANCH {} APPLIED".format(branch))

print("USING GIT BRANCH {}".format(branch))

# before doing anything get the DB setup
read_db()

setup_dirs()

# login to tg and begin to listen for updates in channels
tg_listen()

# handle exit condition
save_db()
