import config
from util.git import add_all_to_git, add_author_to_git

from telegram import Bot

def set_author_for_channel(bot, author, channel_id):
    """
    Creates a relationship between an author and a channel.
    This is maintained in the Bot's DB and is written
    to a file.

    Keyword Arguments:
    bot -- The top level bot. Used to access the DB
    author -- The author to link with the channel with
    channel_id -- The channel to link the author with
    """
    tg_bot = Bot(config.api_token)

    author_doesnt_exist = bot.db.get(author) is None
    channel_doesnt_exist = bot.db.inverse.get(channel_id) is None

    if author_doesnt_exist and channel_doesnt_exist:
        bot.db[author] = channel_id
        bot.save_db()
        add_author_to_git(author)
        tg_bot.sendMessage(
            channel_id, "Author {} Successfully Added".format(author))

        add_all_to_git("Author {} added for channel {}".format(
            author, channel_id))
    elif not author_doesnt_exist and not channel_doesnt_exist:
        tg_bot.sendMessage(
            channel_id, "Author {} and Channel {} already added".format(author, channel_id))
    elif not author_doesnt_exist:
        tg_bot.sendMessage(channel_id, "Author {} already added in a different channel ({})".format(
            author, bot.db.get(author)))
    elif not channel_doesnt_exist:
        tg_bot.sendMessage(channel_id, "Channel {} already added for a different author ({})".format(
            channel_id, bot.db.inverse.get(channel_id)))