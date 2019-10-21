import os
import re
import subprocess

def update_git(git_dir: str, group_id: int, git_url: str):
    folder_name = "g" + str(group_id)
    group_dir = os.path.join(git_dir, folder_name)
    if not os.path.exists(group_dir):
        os.makedirs(group_dir)
    project_name = re.search(r"/([^/]+)\.git", git_url).group(1)
    if not os.path.exists(os.path.join(group_dir, project_name)):
        clone_cmd = "git clone " + git_url
        pr = subprocess.Popen("/usr/bin/"+clone_cmd , cwd=group_dir, \
            shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        (out, error) = pr.communicate()
        print(out, error)


# update_git(git_dir=".", group_id="10", git_url="git@gitlab.com:svafaiet/dummyproject.git")
