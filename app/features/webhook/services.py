import subprocess
from datetime import datetime, timezone

from flask import abort
from splent_framework.services.BaseService import BaseService

import docker
from app.features.webhook.repositories import WebhookRepository

# Resolved on first use rather than at import. The plain production stack has
# no Docker socket, and an import-time client made every app that loads this
# feature require one just to boot; only the webhook deployment compose mounts
# the socket. Tests inject a fake by assigning this module attribute directly.
client = None


def _docker_client():
    global client
    if client is None:
        client = docker.from_env()
    return client


class WebhookService(BaseService):
    def __init__(self):
        super().__init__(WebhookRepository())

    def get_web_container(self):
        try:
            return _docker_client().containers.get("web_app_container")
        except docker.errors.NotFound:
            abort(404, description="Web container not found.")

    def get_volume_name(self, container):
        volume_name = next(
            (
                mount.get("Name") or mount.get("Source")
                for mount in container.attrs["Mounts"]
                if mount["Destination"] == "/workspace"
            ),
            None,
        )

        if not volume_name:
            raise ValueError("No volume or bind mount found mounted on /workspace")

        return volume_name

    def execute_host_command(self, volume_name, command):
        try:
            subprocess.run(
                [
                    "docker",
                    "run",
                    "--rm",
                    "-v",
                    f"{volume_name}:/workspace",
                    "-v",
                    "/var/run/docker.sock:/var/run/docker.sock",
                    "-w",
                    "/workspace",
                    *command,
                ],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            abort(500, description=f"Host command failed: {str(e)}")

    def execute_container_command(self, container, command, workdir="/workspace"):
        exit_code, output = container.exec_run(command, workdir=workdir)
        if exit_code != 0:
            abort(500, description=f"Container command failed: {output.decode('utf-8')}")
        return output.decode("utf-8")

    def log_deployment(self, container):
        log_entry = f"Deployment successful at {datetime.now(timezone.utc).isoformat()}\n"
        log_file_path = "/workspace/deployments.log"
        self.execute_container_command(container, f"sh -c 'echo \"{log_entry}\" >> {log_file_path}'")

    def restart_container(self, container):
        subprocess.Popen(["/bin/sh", "/workspace/scripts/restart_container.sh", container.id])

    def deploy(self) -> None:
        """End-to-end deploy: pull latest, refresh deps, migrate, log, restart."""
        container = self.get_web_container()
        self.execute_container_command(container, "/workspace/scripts/git_update.sh")
        self.execute_container_command(container, "pip install -r requirements.txt")
        self.execute_container_command(container, "flask db upgrade")
        self.log_deployment(container)
        self.restart_container(container)
