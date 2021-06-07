import os

from config import config, AUTHOR_DIR

def switch_branch(branch = config.git_dir):
    """ 
    Change to the git branch as specified

    Keyword Arguments:
    branch -- The git branch to switch to
    """
    wd = os.getcwd()
    os.chdir(config.git_dir)
    os.system("git checkout {}".format(branch))
    os.chdir(wd)

def add_all_to_git(msg):
    """ 
    Add all of the changed files to git and commit them

    Keyword Arguments:
    msg -- The commit message for this git transaction
    """
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
    """ 
    Create directory in the Buzzard repo for the specified author 
    
    Keyword Arguments:
    author -- The name of the author to add to the Buzzard Repo
    """
    author_dir = AUTHOR_DIR.format(author)
    if not os.path.exists(author_dir):
        os.mkdir(author_dir)
