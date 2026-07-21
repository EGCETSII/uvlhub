"""Service-level tests for webhook — deploy() orchestration with stubbed effects.

``WebhookService.deploy`` pulls code, reinstalls dependencies, migrates the
database and restarts the container. Every one of those effects is replaced by
a recorder here: these tests assert *which* commands would be issued and in
what order, and never let a real deployment run.
"""

import pytest
from werkzeug.exceptions import HTTPException

from app.features.webhook import services as webhook_services
from app.features.webhook.services import WebhookService

pytestmark = pytest.mark.service

EXPECTED_COMMANDS = [
    "/workspace/scripts/git_update.sh",
    "pip install -r requirements.txt",
    "flask db upgrade",
]


class RecordingContainer:
    """Stands in for the docker container; records commands, runs nothing."""

    def __init__(self, container_id="web-container", failing_command=None):
        self.id = container_id
        self.attrs = {"Mounts": [{"Destination": "/workspace", "Name": "workspace_volume"}]}
        self.commands = []
        self.failing_command = failing_command

    def exec_run(self, command, workdir="/workspace"):
        self.commands.append(command)
        if self.failing_command and command.startswith(self.failing_command):
            return 1, b"command exploded"
        return 0, b"ok"


@pytest.fixture
def deploy_harness(monkeypatch):
    """Service wired to a recording container with subprocess fully stubbed."""
    container = RecordingContainer()
    popen_calls = []

    monkeypatch.setattr(
        webhook_services,
        "client",
        type("FakeClient", (), {"containers": type("C", (), {"get": staticmethod(lambda name: container)})()})(),
    )
    monkeypatch.setattr(webhook_services.subprocess, "Popen", lambda argv: popen_calls.append(argv))
    monkeypatch.setattr(
        webhook_services.subprocess,
        "run",
        lambda *args, **kwargs: pytest.fail("deploy() must not run host subprocesses"),
    )

    return WebhookService(), container, popen_calls


def test_deploy_issues_commands_in_order(test_app, deploy_harness):
    service, container, popen_calls = deploy_harness

    with test_app.app_context():
        service.deploy()

    assert container.commands[:3] == EXPECTED_COMMANDS
    assert len(container.commands) == 4
    assert container.commands[3].startswith("sh -c 'echo \"Deployment successful at ")
    assert "/workspace/deployments.log" in container.commands[3]


def test_deploy_restarts_container_last(test_app, deploy_harness):
    service, container, popen_calls = deploy_harness

    with test_app.app_context():
        service.deploy()

    assert popen_calls == [["/bin/sh", "/workspace/scripts/restart_container.sh", "web-container"]]


@pytest.mark.parametrize(
    "failing_command, expected_commands",
    [
        ("/workspace/scripts/git_update.sh", EXPECTED_COMMANDS[:1]),
        ("pip install -r requirements.txt", EXPECTED_COMMANDS[:2]),
        ("flask db upgrade", EXPECTED_COMMANDS[:3]),
    ],
)
def test_deploy_stops_at_first_failing_command(test_app, monkeypatch, failing_command, expected_commands):
    container = RecordingContainer(failing_command=failing_command)
    popen_calls = []
    monkeypatch.setattr(
        webhook_services,
        "client",
        type("FakeClient", (), {"containers": type("C", (), {"get": staticmethod(lambda name: container)})()})(),
    )
    monkeypatch.setattr(webhook_services.subprocess, "Popen", lambda argv: popen_calls.append(argv))
    service = WebhookService()

    with test_app.app_context():
        with pytest.raises(HTTPException) as excinfo:
            service.deploy()

    assert excinfo.value.code == 500
    assert "command exploded" in excinfo.value.description
    # Nothing after the failure ran, and the container was never restarted.
    assert container.commands == expected_commands
    assert popen_calls == []


def test_deploy_aborts_404_when_web_container_is_missing(test_app, monkeypatch):
    import docker

    def missing(name):
        raise docker.errors.NotFound("no such container")

    monkeypatch.setattr(
        webhook_services,
        "client",
        type("FakeClient", (), {"containers": type("C", (), {"get": staticmethod(missing)})()})(),
    )
    monkeypatch.setattr(
        webhook_services.subprocess,
        "Popen",
        lambda argv: pytest.fail("must not restart when the container is missing"),
    )
    service = WebhookService()

    with test_app.app_context():
        with pytest.raises(HTTPException) as excinfo:
            service.deploy()

    assert excinfo.value.code == 404
