import os
import sys

from jinja2 import Environment, FileSystemLoader
from pytz import timezone

# TODO this desperately needs to be handled via command line args

BUZZARD_GIT_DIR = "../../BUZZARD"
BUZZARD_BOT_DIR = BUZZARD_GIT_DIR + "/.tg_bot"
DB_FILE = BUZZARD_BOT_DIR + "/db.json"
AUTHOR_DIR = BUZZARD_GIT_DIR + "/consumption/{}"
PT = timezone("America/Los_Angeles")

ALLOWED_AUTHORS = ["cj", "jonbo", "gorum", "kristen", "shahruz"]

templateLoader = FileSystemLoader(searchpath="../templates")
env = Environment(loader=templateLoader)

class BotConfig():

  def __init__(self):
    self.git_dir = BUZZARD_GIT_DIR
    self.bot_dir = BUZZARD_BOT_DIR
    self.db_file = DB_FILE
    self.api_token = self._get_api_token()
    self.git_branch = self._set_git_branch()

    self._print_config()

  def _print_config(self):
    print("========== CONFIG ==========\n")
    print("GIT DIR:", self.git_dir)
    print("BOT DIR:", self.bot_dir)
    print("DB FILE:", self.db_file)
    print("GIT BRANCH:", self.git_branch)
    print("\n======== END CONFIG ========\n")

  def _get_api_token(self):
      # make sure we have an API token for the bot
      api_token = os.getenv('BUZZARD_TG_BOT_TOKEN')
      if api_token is None:
          raise Exception("BUZZARD_TG_BOT_TOKEN ENVIRONMENT VARIABLE IS NOT SET")
      
      return api_token

  def _set_git_branch(self):
    branch = "main"

    if len(sys.argv) == 2:
        if sys.argv[1] == "test" or sys.argv[1] == "main":
            branch = sys.argv[1]
        else:
            raise Exception("INCORRECT BRANCH {} APPLIED".format(branch))

    return branch
  
config = BotConfig()
