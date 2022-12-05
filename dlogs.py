from collections import namedtuple
from subprocess import run

from flask import Flask

Container = namedtuple("Container", "id image container")
app = Flask(__name__)


@app.route("/")
def index():
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
        "</style></head><body>",
    ]
    for container in containers:
        html.append(
            f"<div><a href='/logs/{container.id}'>"
            f"{container.image} // {container.container}</a></div>"
        )
    html += ["</body></html>"]
    return "\n".join(html)


@app.route("/logs/<id_>")
def logs(id_):
    log = run(
        f"docker logs --timestamps --tail 500 {id_}", shell=True, capture_output=True
    )
    log = log.stdout.decode("utf8").split("\n")
    log.reverse()
    log = "\n".join(log)
    return f"<pre>{log}</pre>"
