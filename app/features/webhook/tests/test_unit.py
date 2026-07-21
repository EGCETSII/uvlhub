"""Unit tests for the webhook feature — pure logic, no Flask app, no DB.

Every side effect (docker client, subprocess) is stubbed: nothing here may
start a container, touch the docker socket or run a real deployment command.
"""

import subprocess

import pytest
from werkzeug.exceptions import HTTPException

import docker
from app.features.webhook import services as webhook_services
from app.features.webhook.services import WebhookService

pytestmark = pytest.mark.unit


class FakeContainer:
    """Records ``exec_run`` calls instead of executing anything."""

    def __init__(self, container_id="container-id", mounts=None, failures=None):
        self.id = container_id
        self.attrs = {"Mounts": mounts or []}
        self.calls = []
        self.failures = failures or {}

    def exec_run(self, command, workdir="/workspace"):
        self.calls.append((command, workdir))
        for prefix, output in self.failures.items():
            if command.startswith(prefix):
                return 1, output
        return 0, b"ok"


def test_get_volume_name_returns_named_volume():
    service = WebhookService()
    container = FakeContainer(
        mounts=[
            {"Destination": "/etc/hosts", "Name": "other"},
            {"Destination": "/workspace", "Name": "uvlhub_workspace"},
        ]
    )

    assert service.get_volume_name(container) == "uvlhub_workspace"


def test_get_volume_name_falls_back_to_bind_mount_source():
    service = WebhookService()
    container = FakeContainer(mounts=[{"Destination": "/workspace", "Source": "/host/uvlhub"}])

    assert service.get_volume_name(container) == "/host/uvlhub"


def test_get_volume_name_raises_when_workspace_not_mounted():
    service = WebhookService()
    container = FakeContainer(mounts=[{"Destination": "/data", "Name": "data"}])

    with pytest.raises(ValueError, match="/workspace"):
        service.get_volume_name(container)


def test_get_web_container_returns_container_from_client(monkeypatch):
    service = WebhookService()
    container = FakeContainer()

    class FakeContainers:
        def get(self, name):
            assert name == "web_app_container"
            return container

    monkeypatch.setattr(webhook_services, "client", type("C", (), {"containers": FakeContainers()})())

    assert service.get_web_container() is container


def test_get_web_container_aborts_404_when_missing(monkeypatch):
    service = WebhookService()

    class FakeContainers:
        def get(self, name):
            raise docker.errors.NotFound("no such container")

    monkeypatch.setattr(webhook_services, "client", type("C", (), {"containers": FakeContainers()})())

    with pytest.raises(HTTPException) as excinfo:
        service.get_web_container()
    assert excinfo.value.code == 404


def test_execute_container_command_returns_decoded_output():
    service = WebhookService()
    container = FakeContainer()

    output = service.execute_container_command(container, "flask db upgrade")

    assert output == "ok"
    assert container.calls == [("flask db upgrade", "/workspace")]


def test_execute_container_command_passes_custom_workdir():
    service = WebhookService()
    container = FakeContainer()

    service.execute_container_command(container, "ls", workdir="/tmp")

    assert container.calls == [("ls", "/tmp")]


def test_execute_container_command_aborts_500_on_non_zero_exit():
    service = WebhookService()
    container = FakeContainer(failures={"flask db upgrade": b"migration boom"})

    with pytest.raises(HTTPException) as excinfo:
        service.execute_container_command(container, "flask db upgrade")

    assert excinfo.value.code == 500
    assert "migration boom" in excinfo.value.description


def test_execute_host_command_builds_docker_run_invocation(monkeypatch):
    service = WebhookService()
    recorded = {}

    def fake_run(argv, check):
        recorded["argv"] = argv
        recorded["check"] = check

    monkeypatch.setattr(webhook_services.subprocess, "run", fake_run)

    service.execute_host_command("uvlhub_workspace", ["git", "pull"])

    assert recorded["check"] is True
    assert recorded["argv"] == [
        "docker",
        "run",
        "--rm",
        "-v",
        "uvlhub_workspace:/workspace",
        "-v",
        "/var/run/docker.sock:/var/run/docker.sock",
        "-w",
        "/workspace",
        "git",
        "pull",
    ]


def test_execute_host_command_aborts_500_when_subprocess_fails(monkeypatch):
    service = WebhookService()

    def fake_run(argv, check):
        raise subprocess.CalledProcessError(returncode=2, cmd=argv)

    monkeypatch.setattr(webhook_services.subprocess, "run", fake_run)

    with pytest.raises(HTTPException) as excinfo:
        service.execute_host_command("vol", ["git", "pull"])

    assert excinfo.value.code == 500
    assert "Host command failed" in excinfo.value.description


def test_log_deployment_appends_to_workspace_log():
    service = WebhookService()
    container = FakeContainer()

    service.log_deployment(container)

    assert len(container.calls) == 1
    command, workdir = container.calls[0]
    assert workdir == "/workspace"
    assert command.startswith("sh -c 'echo \"Deployment successful at ")
    assert command.endswith(">> /workspace/deployments.log'")


def test_restart_container_spawns_restart_script(monkeypatch):
    service = WebhookService()
    container = FakeContainer(container_id="deadbeef")
    recorded = {}

    monkeypatch.setattr(webhook_services.subprocess, "Popen", lambda argv: recorded.setdefault("argv", argv))

    service.restart_container(container)

    assert recorded["argv"] == ["/bin/sh", "/workspace/scripts/restart_container.sh", "deadbeef"]
