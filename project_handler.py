from utils import run_cmd
from git_handler import update_git
import re
import uuid
import docker
import os
from shutil import copyfile
from configuration import MAX_MEMORY_CONTESTANT, BASE_DIR

import logger

SUCCESSFUL_STEP_REGEX = r"(\s*--->[^-]+)+"
COPY_REQUIREMENTS_REGEX = r"COPY requirements\.txt $DIR/"
INSTALL_REQUIREMENTS_REGEX = r"RUN pip install -r requirements\.txt"
ERROR_REGEX = r"ERROR:"


class ContestantProjectHandler:
    CONTESTANT_SETTINGS_NAME = "server_settings.py"
    CONTESTANT_SETTINGS_PATH = os.path.join(BASE_DIR, "templates", CONTESTANT_SETTINGS_NAME)

    def __init__(self):
        self.client = docker.from_env()

    def setup(self, repo_dir: str, group_id: str, git_url: str):
        project_dir = update_git(root_dir=repo_dir, group_id=group_id, git_url=git_url)
        try:
            copyfile(
                ContestantProjectHandler.CONTESTANT_SETTINGS_PATH,
                os.path.join(project_dir, ContestantProjectHandler.CONTESTANT_SETTINGS_NAME)
            )
        except Exception:
            logger.log_error("Could not copy django settings for group {}".format(group_id))
            raise Exception("Could not copy django settings")
        out, error = run_cmd(cmd="./scripts/remove_migrations.sh " + project_dir, directory=".")  # TODO handle logs
        if len(error) != 0:
            logger.log_info("error in removing migrations: {}".format(str(out)))
        out, error = run_cmd(cmd="./scripts/build_image.sh " + project_dir, directory=".")
        build_msg = out.decode("utf-8")
        logger.log_info("Project for group {} build successfully with message: {}".format(group_id, build_msg))
        try:
            image_id = re.search(r"Successfully built ((\w|\d)+)\n", build_msg).group(1)
        except Exception:
            if re.findall(COPY_REQUIREMENTS_REGEX, build_msg) is not None and re.findall(
                    INSTALL_REQUIREMENTS_REGEX, build_msg) is None:
                logger.log_warn("Could not find requirements.txt for group {}".format(group_id))
                raise Exception("Could not find requirements.txt file")

            if re.findall(INSTALL_REQUIREMENTS_REGEX + SUCCESSFUL_STEP_REGEX + ERROR_REGEX, build_msg) is not None:
                logger.log_warn("Could not install requirements for group {}".format(group_id))
                raise Exception("Could not install requirements")
            logger.log_warn("Failed to build docker image for group {}.".format(group_id))
            raise Exception("Failed to build docker image")

        try:
            os.remove(os.path.join(project_dir, ContestantProjectHandler.CONTESTANT_SETTINGS_NAME))
        except Exception:
            logger.log_error("Could not remove django settings for group {}".format(group_id))
            raise Exception("Could not remove django settings")

        logger.log_success("Image built for team {} successfully".format(group_id))
        return image_id

    def run(self, image_id: str, port: int):
        container_name = "webelopers_" + str(port)
        try:
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
            logger.log_success(
                "Project is running on container {} with id {} for image {}".format(container_name, result, image_id))
            return container_name
        except Exception as e:
            logger.log_warn("Could not run container {}".format(container_name))
            raise Exception("Could not run docker")

    def kill(self, container_name: str):
        self.client.containers.get(container_name).stop()
        logger.log_info("Killing container {}...".format(container_name))


DEFAULT_PROJECT_HANDLER = ContestantProjectHandler()
