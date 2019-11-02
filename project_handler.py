from utils import run_cmd
from git_handler import update_git
import re
import uuid
import docker
import os
from shutil import copyfile
from configuration import MAX_MEMORY_CONTESTANT, BASE_DIR


class ContestantProjectHandler:
    CONTESTANT_SETTINGS_NAME = "server_settings.py"
    CONTESTANT_SETTINGS_PATH = os.path.join(BASE_DIR, "templates", CONTESTANT_SETTINGS_NAME)

    def __init__(self):
        self.client = docker.from_env()

    def setup(self, repo_dir: str, group_id: int, git_url: str):
        project_dir = update_git(root_dir=repo_dir, group_id=group_id, git_url=git_url)

        copyfile(
            ContestantProjectHandler.CONTESTANT_SETTINGS_PATH,
            os.path.join(project_dir, ContestantProjectHandler.CONTESTANT_SETTINGS_NAME)
        )

        out, error = run_cmd(cmd="./scripts/build_image.sh " + project_dir, directory=".")
        build_msg = out.decode("utf-8")
#        TODO: check different error types: requirements.txt, ...
        try:
            image_id = re.search(r"Successfully built ((\w|\d)+)\n", build_msg).group(1)
        except:
            logger.log_error("failed to build docker image. exiting.")
            exit(1)

        os.remove(os.path.join(project_dir, ContestantProjectHandler.CONTESTANT_SETTINGS_NAME))

        print(image_id)
        # handle error requirements.txt: no such file or directory
        return image_id

    def run(self, image_id: str, port: int):
        container_name = "webelopers" + str(uuid.uuid1())
        result = self.client.containers.run(
            image=image_id,
            detach=True,
            auto_remove=True,
            mem_limit=str(MAX_MEMORY_CONTESTANT) + "m",
            mem_reservation=str(MAX_MEMORY_CONTESTANT // 2) + "m",
            name=container_name,
            oom_kill_disable=False,
            ports={"8000": port},

        )
        # run_cmd(cmd="./scripts/run_container.sh " + container_name + " " + image_id, directory=".")
        print("server_is_up")
        print(result)
        return container_name

    def kill(self, container_name: str):
        self.client.containers.get(container_name).stop()
        # return run_cmd(cmd="./scripts/stop_container.sh " + container_name, directory=".")


DEFAULT_PROJECT_HANDLER = ContestantProjectHandler()

# import os
#
# proj = ContestantProjectHandler()
# img_hash = proj.setup(os.environ['HOME'] + "/temp", 10, "git@git.edu.sharif.edu:webelopers2019/terminator.git")
# container_name = proj.run(img_hash, 8000)
# proj.kill(img_hash)
