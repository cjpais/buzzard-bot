import os
import sys

from jinja2 import Environment, FileSystemLoader
from pytz import timezone

# TODO this desperately needs to be handled via command line args

BUZZARD_GIT_DIR = "../../BUZZARD"
BUZZARD_BOT_DIR = "{}/.tg_bot"
DB_FILE = "{}/db.json"
AUTHOR_DIR = BUZZARD_GIT_DIR + "/consumption/{}"
BUZZARD_GIT_SSH = "git@github.com:calculator/BUZZARD.git"
PT = timezone("America/Los_Angeles")

ALLOWED_AUTHORS = ["cj", "jonbo", "gorum", "kristen", "shahruz"]

templateLoader = FileSystemLoader(searchpath="../templates")
env = Environment(loader=templateLoader)

class BotConfig():
  """
  A class which sets up the configuration for the Bot.
  This is intended to be a Singleton, where other modules
  import this file to get the config.

  Member Variables:
  git_dir -- The relative path to the BUZZARD git directory on the computer
  bot_dir -- The path to the hidden bot data inside the BUZZARD git repo
  db_file -- The path to the DB file stored in the BUZZARD git repo
  api_token -- The BuzzardBot's API Token
  git_branch -- The working Git branch to use
  """

  def __init__(self):
    """ Initializes the Bot's Config """
    self.git_dir = self._set_buzzard_git_dir()
    self.bot_dir = BUZZARD_BOT_DIR.format(self.git_dir)
    self.db_file = DB_FILE.format(self.bot_dir)
    self.api_token = self._get_api_token()
    self.git_branch = self._set_git_branch()

    self._print_config()

  def _print_config(self):
    """ Helper function to print important config variables """
    print("========== CONFIG ==========\n")
    print("GIT DIR:", self.git_dir)
    print("BOT DIR:", self.bot_dir)
    print("DB FILE:", self.db_file)
    print("GIT BRANCH:", self.git_branch)
    print("\n======== END CONFIG ========\n")

  def _get_api_token(self):
    """ 
    Helper function to get the Telegram API token from the local
    environment variables
    """

    # make sure we have an API token for the bot
    api_token = os.getenv('BUZZARD_TG_BOT_TOKEN')
    if api_token is None:
        raise Exception("BUZZARD_TG_BOT_TOKEN ENVIRONMENT VARIABLE IS NOT SET")
    
    return api_token

  def _set_buzzard_git_dir(self):
    """ 
    Helper function to set the directory of the BUZZARD git repo from 
    command line arguments
    """
    dir = BUZZARD_GIT_DIR

    if len(sys.argv) >= 3:
      dir = sys.argv[2]

    return dir

  def _set_git_branch(self):
    """ Helper function to set the git branch from command line arguments """
    branch = "main"

    if len(sys.argv) >= 2:
        if sys.argv[1] == "test" or sys.argv[1] == "main":
            branch = sys.argv[1]
        else:
            raise Exception("INCORRECT BRANCH {} APPLIED".format(branch))

    return branch
  
config = BotConfig()
