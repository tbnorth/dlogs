"""Simple web-app to show logs of containers running on the same system."""

from collections import namedtuple
from subprocess import run

from flask import Flask

Container = namedtuple("Container", "id image container")
app = Flask(__name__)


@app.route("/")
def index():
    """Show list of containers with links to logs."""
    containers = run(
        "docker ps --format '{{.ID}}\\t{{.Image}}\\t{{.Names}}'",
        shell=True,
        capture_output=True,
    )
    containers = [
        Container(*line.split("\t"))
        for line in containers.stdout.decode("utf8").split("\n")
        if line.strip()
    ]
    containers.sort(key=lambda x: (x.image, x.container))
    html = [
        "<html><head><style>",
        "a {text-decoration:none}",
        "a:hover {text-decoration:underline}",
        "</style></head><body><h3>Select container</h3>",
    ]
    for container in containers:
        html.append(
            f"<div><a href='/logs/{container.id}'>"
            f"{container.image} // {container.container}</a></div>"
        )
    html += ["</body></html>"]
    return "\n".join(html)


def raw_logs(id_):
    """Get log text from container <id_>."""
    log = run(
        f"docker logs --timestamps --tail 5000 {id_}", shell=True, capture_output=True
    )
    return log.stdout.decode("utf8")


@app.route("/raw/<id_>")
def raw(id_):
    """Show logs as plain text suitable for script."""
    return raw_logs(id_)


@app.route("/logs/<id_>")
def logs(id_):
    """Show logs as <pre/> block newest at top of page."""
    log = "\n".join(reversed(raw_logs(id_).split("\n")))
    return f"<pre>{log}</pre>"
