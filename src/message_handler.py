import os
from bot import BuzzardBot

from config import PT, AUTHOR_DIR, env, config, ALLOWED_AUTHORS
from util.git import add_all_to_git
from util.misc import set_author_for_channel

from telegram import Update, Bot

class Message():
    """
    A class containing a bunch of useful variables about a specific
    telegram message

    Member Variables:
    bot -- The overall BuzzardBot instance
    update -- The raw Telegram Update
    tg_bot -- An instance of the Telegram Bot to send messages with
    channel_id -- The channel ID this message came from
    message_id -- The raw message ID from Telegram
    text -- The message body, the raw text the user sent
    date -- The date the message was sent at
    date_string -- A nicer string representation of the date
    reply_id -- If this message was a reply, 
                this is the message that was responded to. Otherwise None
    author -- The associated author with this channel. If no author it is None
    author_dir -- The directory in git for this author. If no author it is None
    """

    def __init__(self, bot, update):
        """ Initializes the Message from the raw Telegram Update """
        self.bot = bot
        self.update = update

        # TODO move this, it is convenient but breaks proper encapsulation
        self.tg_bot = Bot(config.api_token)

        # derive basic info from the update
        self.channel_id = update.channel_post.chat.id
        self.message_id = update.channel_post.message_id
        self.text = update.channel_post.text
        self.date = update.channel_post.date.astimezone(PT)
        self.date_string = self.date.strftime("%x - %-I:%M%p")

        try:
            self.reply_id = update.channel_post.reply_to_message.message_id
        except AttributeError:
            self.reply_id = None

        try:
            self.author = bot.db.inverse[self.channel_id]
            self.author_dir = AUTHOR_DIR.format(self.author)
        except KeyError:
            self.author = None

def dispatch(bot: BuzzardBot, update: Update):
    """
    Takes a Telegram Update delegates to the correct
    function to handle that update.

    Keyword Arguments:
    bot -- The overall BuzzardBot instance
    update -- The raw Telegram Update
    """
    print(update)

    message = Message(bot, update)

    if "/set " in message.text:
        handle_set_command(message)
    elif "/remove " in message:
        handle_remove_command(message)
    else:
        print("message", message.text)
        handle_message(message)

def handle_set_command(message: Message):
    """ Handles /set command. Sets an author in a channel if possible """
    command = message.text
    author = command.replace("/set ", "")

    if author in ALLOWED_AUTHORS or config.git_branch != "main":
        set_author_for_channel(message.bot, author, message.channel_id)
    else:
        message.tg_bot.sendMessage(
            message.channel_id, "Author {} Not Allowed".format(author))

def handle_remove_command(message: Message):
    """ Handles /remove command. Removes an author in a channel if possible """
    pass

def handle_message(message: Message):
    """ Handles any non-command based message. Adds it to the BUZZARD git """
    # make sure there is an author for this message before continuing
    if message.author is None:
        message.tg_bot.send_message(message.channel_id, 
            "No author for channel {}".format(message.channel_id))
        return
    
    if message.reply_id:
        handle_reply_message(message)
    else:
        handle_new_message(message)

    # TODO this should be title eventually
    add_all_to_git("added new content from {}".format(message.author))

def handle_reply_message(message: Message):
    """ 
    For a reply message, this function finds the original message file
    and appends the reply to it 
    """
    # find existing file and append to it instead of creating new file
    dir_files = os.listdir(message.author_dir)

    fn = None
    for df in dir_files:
        file_id = int(df.split("_")[-1].replace('.md', ''))

        if file_id == message.reply_id:
            fn = "{}/{}".format(message.author_dir, df)
            break

    if not fn:
        raise Exception(
            "Could not find message {} for author {}".format(message.reply_id, message.author))

    with open(fn, 'a') as f:
        f.write("\n\n_[{}]:_\n\n{}".format(message.date_string, message))

def handle_new_message(message: Message):
    """ 
    For a mew message, this function creates a message file for the author
    and adds the information to it
    """
    title = ""
    #title = get_url_title(message).replace(" ", "_")
    fn = "{}/{}_{}.md".format(message.author_dir, title[:150], message.message_id)
    with open(fn, 'w') as f:
        template = env.get_template("tg-post.md")
        data = template.render(author=message.author,
                                content=message)
        # content=message,
        # date=date_string)
        f.write(data)