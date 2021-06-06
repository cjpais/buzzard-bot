import os

from config import PT, AUTHOR_DIR, env, config
from util.git import add_all_to_git, add_author_to_git

from telegram import Update, Bot

def handle_message(bot, update: Update):
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

        set_author_for_channel(bot, author, channel_id)
    elif "/remove " in message:
        pass
    else:
        title = ""
        try:
            author = bot.db.inverse[channel_id]
        except KeyError:
            # TODO would it make sense to send a message to the channel instead?
            print("No author for channel {}".format(channel_id))
            return
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
                raise Exception(
                    "Could not find message {} for author {}".format(reply_id, author))

            f = open(fn, 'a')
            f.write("\n\n_[{}]:_\n\n{}".format(date_string, message))
        else:
            #title = get_url_title(message).replace(" ", "_")
            fn = "{}/{}_{}.md".format(author_dir, title[:150], message_id)
            f = open(fn, 'w')

            template = env.get_template("tg-post.md")

            data = template.render(author=author,
                                   content=message)
            # content=message,
            # date=date_string)
            f.write(data)

        f.close()

        # TODO this should be title eventually
        add_all_to_git("added new content from {}".format(author))


def set_author_for_channel(bot, author, channel_id):
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
