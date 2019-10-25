from utils import run_cmd
from git_handler import update_git
import re

def setup(repo_dir: str, group_id: int, git_url: str):
    project_dir = update_git(root_dir=repo_dir, group_id=group_id, git_url=git_url)
    out, error = run_cmd(cmd="./scripts/build_image.sh "+project_dir, directory=".")
    build_msg = out.decode("utf-8")
    print(out)
    print(error)
    image_hash = re.search(r"Successfully built ((\w|\d)+)\n", build_msg).group(1)
    print(image_hash)
    # handle error requirements.txt: no such file or directory
    return image_hash
    
import os
setup(os.environ['HOME']+"/temp", 10, "git@git.edu.sharif.edu:webelopers2019/terminator.git")
