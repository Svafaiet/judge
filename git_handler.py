import os
import re
from utils import run_cmd
import logger


def _run_git(directory: str, git_cmd: str):
    return run_cmd(cmd="/usr/bin/" + git_cmd, directory=directory)


def update_git(root_dir: str, group_id: int, git_url: str):
    folder_name = "g" + str(group_id)
    logger.log_info("updating git for group {} with git url {} initiated".format(group_id, git_url))
    group_dir = os.path.join(root_dir, folder_name)
    if not os.path.exists(group_dir):
        os.makedirs(group_dir)
        logger.log_info("making directory for group")
    if not re.match(r"((git|ssh|http(s)?)|(git@[\w.]+))(:(//)?)([\w.@:/\-~]+)(\.git)(/)?", git_url):
        logger.log_log("git url for team with id {} is not valid: {}".format(group_id, git_url))
        raise Exception("Invalid git url")
    project_name = re.search(r"/([^/]+)\.git", git_url).group(1)
    if not os.path.exists(os.path.join(group_dir, project_name)):
        logger.log_info("cloning into repository {}".format(git_url))
        clone_cmd = "git clone " + git_url
        out, error = _run_git(group_dir, clone_cmd)
        if len(out) != 0:
            logger.log_info("In cloning process for group {}: {}".format(group_id, out))
        if len(error) != 0:
            logger.log_log("Cloning into repository {} failed with error: {}".format(git_url, str(error)))
            raise Exception("Failed while Cloning the Project")
        print("result: ", out, "\nerror: ", error, "\n")
    else:
        print("Project already exists")
    project_dir = os.path.join(group_dir, project_name, )
    checkout_cmd = "git checkout master"
    out, error = _run_git(project_dir, checkout_cmd)
    print("result: ", out, "\nerror: ", error, "\n")
    pull_cmd = "git pull origin"
    out, error = _run_git(project_dir, pull_cmd)
    print("result: ", out, "\nerror: ", error, "\n")
    reset_origin_cmd = "git reset origin master"
    out, error = _run_git(project_dir, reset_origin_cmd)
    print("result: ", out, "\nerror: ", error, "\n")
    clean_cmd = "git clean -fd"
    out, error = _run_git(project_dir, clean_cmd)
    print("result: ", out, "\nerror: ", error, "\n")
    return project_dir

# update_git(root_dir=".", group_id="10", git_url="git@git.edu.sharif.edu:svafaiet/dummyproject.git")
