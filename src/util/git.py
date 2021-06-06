import os

from config import config, AUTHOR_DIR

def switch_branch():
    wd = os.getcwd()
    os.chdir(config.git_dir)
    os.system("git checkout {}".format(config.git_branch))
    os.chdir(wd)

def add_all_to_git(msg):
    wd = os.getcwd()
    os.chdir(config.git_dir)
    os.system("git checkout {}".format(config.git_branch))
    os.system("git pull origin {}".format(config.git_branch))
    os.system("git add consumption/*")
    os.system("git add .tg_bot/*")
    os.system('git commit -m "{}"'.format(msg))
    os.system("git push origin {}".format(config.git_branch))
    os.chdir(wd)

def add_author_to_git(author):
    author_dir = AUTHOR_DIR.format(author)
    if not os.path.exists(author_dir):
        os.mkdir(author_dir)
