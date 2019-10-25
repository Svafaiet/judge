import os
import re
import subprocess
from utils import run_cmd

def _run_git(directory: str, git_cmd: str):
    return run_cmd(cmd="/usr/bin/"+git_cmd, directory=directory)

def update_git(root_dir: str, group_id: int, git_url: str):
    folder_name = "g" + str(group_id)
    group_dir = os.path.join(root_dir, folder_name)
    if not os.path.exists(group_dir):
        os.makedirs(group_dir)
    project_name = re.search(r"/([^/]+)\.git", git_url).group(1)
    # TODO validate git url 
    if not os.path.exists(os.path.join(group_dir, project_name)):
        print("cloning")
        clone_cmd = "git clone " + git_url
        out, error = _run_git(group_dir, clone_cmd)
        print("result: ", out, "\nerror: ", error, "\n")
        # TODO handle git errors here and after that
    else:
        print("Project already exists")
    project_dir = os.path.join(group_dir, project_name)
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
