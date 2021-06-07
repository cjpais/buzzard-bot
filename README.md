# buzzard-bot

The goal is to take every message sent to a Telegram Channel and
post it on [BUZZARD](https://buzzard.life)

## Code Overview (/src)

* `bot.py`
  * The top level module. Runs the whole Telegram Bot
* `config.py`
  * Holds basic configuration information
* `message_handler.py`
  * Handles the incoming messages
* `util/`
  * `git.py`
    * Functions dealing with Git operations
  * `url.py`
    * Functions dealing with URL's
  * `misc.py`
    * Miscellaneous functions that don't belong in the other modules

## Starting the Bot

### Preparation

Before starting the bot there are a few requirements.

1. Have a telegram bot API key
2. Have write access to BUZZARD git repo
3. Clone the BUZZARD Repo

Once these requirements are gathered, you can feasibly start the bot.

Before running it you will need to set your API key as an linux environment variable.
The suggested way to do this is add the following to your `.bashrc` or `.zshrc`

**BASH**
`echo export BUZZARD_TG_BOT_TOKEN="<YOUR_API_TOKEN>" >> ~/.bashrc`

**ZSH**
`echo export BUZZARD_TG_BOT_TOKEN="<YOUR_API_TOKEN>" >> ~/.zshrc`

Please note the environment variable name must be `BUZZARD_TG_BOT_TOKEN`

### Running it

There are multiple ways to run the bot.

You can either run it on the "main" or "test" branch of BUZZARD.
You will also need to point it at your cloned BUZZARD Repo.

* "main" - `python3 src/bot.py main <BUZZARD_REPO_PATH>`
* "test" - `python3 src/bot.py test <BUZZARD_REPO_PATH>`

## Set-Up the Bot in Telegram Channel

This lends itself to a few steps:

* Create the Telegram Channel
* Add the @BuzzardBot as an admin of the channel
* Set the author of the channel
* Begin posting

### More Detailed Set-up Instructions

* #### [Video](https://buzzard.life/games/BUZZARD-04/cj/6)
* #### [Text Steps](https://buzzard.life/games/BUZZARD-04/cj/7)
* #### [Photo Walkthrough](https://buzzard.life/games/BUZZARD-04/cj/8)