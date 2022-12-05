"""Simple web-app to show logs of containers running on the same system."""

from collections import namedtuple
from html import escape
from subprocess import run

from flask import Flask, Response

Container = namedtuple("Container", "id image container")
app = Flask(__name__)


def containers():
    """Get list of containers."""
    running = run(
        "docker ps --format '{{.ID}}\\t{{.Image}}\\t{{.Names}}'",
        shell=True,
        capture_output=True,
    )
    running = [
        Container(*line.split("\t"))
        for line in running.stdout.decode("utf8").split("\n")
        if line.strip()
    ]
    running.sort(key=lambda x: (x.container, x.image))
    return running


@app.route("/")
def index():
    """Show list of containers with links to logs."""
    html = [
        "<html><head><style>",
        "a {text-decoration:none}",
        "a:hover {text-decoration:underline}",
        "</style></head><body><h3>Select container</h3>",
    ]
    for container in containers():
        html.append(
            f"<div><a href='/logs/{container.id}'>"
            f"{container.container} // {container.image}</a></div>"
        )
    html += ["</body></html>"]
    return "\n".join(html)


def raw_logs(id_):
    """Get log text from container <id_>."""
    if not any(i.id == id_ or i.container == id_ for i in containers()):
        # Guard against injection
        print("Saw non-existent container ID")
        return "Container ID not found."
    log = run(
        f"docker logs --timestamps --tail 5000 {id_}", shell=True, capture_output=True
    )
    # `docker logs` splits output between stderr and stdout, so merge it.
    logs = log.stderr.decode("utf8").split("\n")
    logs += log.stdout.decode("utf8").split("\n")
    logs.sort()
    return "\n".join(i for i in logs if i.strip())


@app.route("/raw/<id_>")
def raw(id_):
    """Show logs as plain text suitable for script."""
    # Make plain text because if a container's logging XSS requests like <script>do bad
    # thing</script> we don't want that to be HTML in this response.
    return Response(raw_logs(id_), mimetype="text/plain")


@app.route("/logs/<id_>")
def logs(id_):
    """Show logs as <pre/> block newest at top of page."""
    log = "\n".join(reversed(raw_logs(id_).split("\n")))
    if not log.strip():
        log = "(nothing logged by this container)"
    # Escape because if a container's logging XSS requests like <script>do bad
    # thing</script> we don't want that unescaped in this response.
    log = escape(log)
    return f"<pre>{log}</pre>"
