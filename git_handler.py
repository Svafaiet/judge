import os
import re
from utils import run_cmd
import logger

GIT_CLONE_ERROR_REGEX = r"Please make sure you have the correct access rights"
GIT_CHECKOUT_ERROR_REGEX = r"Aborting"


def _run_git(directory: str, git_cmd: str):
    return run_cmd(cmd="/usr/bin/" + git_cmd, directory=directory)


def update_git(root_dir: str, group_id: str, git_url: str, branch_name="master"):
    folder_name = "g_" + group_id
    logger.log_info("updating git for group {} with git url {} initiated".format(group_id, git_url))
    group_dir = os.path.join(root_dir, folder_name)
    if not os.path.exists(group_dir):
        os.makedirs(group_dir)
        logger.log_info("making directory for group")
    if not re.match(r"((git|ssh|http(s)?)|(git@[\w.]+))(:(//)?)([\w.@:/\-~]+)(\.git)(/)?", git_url):
        logger.log_log("git url for team with id {} is not valid: {}".format(group_id, git_url))
        raise Exception("Invalid git url")
    try:
        project_name = re.search(r"/([^/]+)\.git", git_url).group(1)
    except Exception as e:
        logger.log_warn("Could not find project name in {}".format(git_url))
        raise Exception("Unable to find git url")
    if not os.path.exists(os.path.join(group_dir, project_name)):
        logger.log_info("Cloning into repository {}".format(git_url))
        clone_cmd = "git clone " + git_url
        out, error = _run_git(group_dir, clone_cmd)
        if len(out) != 0:
            logger.log_info("In cloning process for group {}: {}".format(group_id, out))
        if len(error) != 0 and re.match(GIT_CLONE_ERROR_REGEX, str(error)):
            logger.log_log("Cloning into repository {} failed with error: {}".format(git_url, str(error)))
            raise Exception("Failed while Cloning the Project")
    else:
        logger.log_info("GIT: Project already exists {}".format(project_name))
    project_dir = os.path.join(group_dir, project_name)
    if not os.path.exists(os.path.join(project_dir, ".git")):
        logger.log_warn("GIT: Project folder {} dont have a .git. initiating git".format(project_dir))
        init_cmd = "git_init"
        _run_git(project_dir, init_cmd)  # TODO log errors
    else:
        rename_origin_cmd = "git remote rename origin old-origin"
        _run_git(project_dir, rename_origin_cmd)  # TODO log errors
    add_origin = "git remote add origin " + git_url
    _run_git(project_dir, add_origin)  # TODO log error
    checkout_cmd = "git checkout " + branch_name
    out, error = _run_git(project_dir, checkout_cmd)
    if len(error) != 0 and re.match(GIT_CHECKOUT_ERROR_REGEX, str(error)):
        logger.log_warn(
            "GIT: Failed to checkout {} in project {} with error: {}".format(branch_name, project_name, str(error)))
    pull_cmd = "git pull origin " + branch_name
    out, error = _run_git(project_dir, pull_cmd)
    if len(error) != 0:
        logger.log_log("GIT: MSG while pulling {} with error: {}".format(project_name, str(error)))
        # raise Exception("Failed while pulling")
    reset_origin_cmd = "git reset --hard origin/" + branch_name
    out, error = _run_git(project_dir, reset_origin_cmd)
    if len(error) != 0:
        logger.log_warn(
            "GIT: Failed while reseting branch {} in project {} with error: {}".format(branch_name, project_name,
                                                                                       str(error)))
        # raise Exception("Failed while reseting branch")
    clean_cmd = "git clean -fd"
    out, error = _run_git(project_dir, clean_cmd)
    if len(error) != 0:
        logger.log_warn("GIT: Failed while cleaning git in project {} with error: {}".format(project_name, str(error)))
        # raise Exception("Failed while cleaning")
    logger.log_info("Updated git for project {} successfully".format(project_name))
    return project_dir
