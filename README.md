# dlogs

Simple web-app to show logs of containers running on the same system.

See list of containers linked to logs

    <your_host>:<your_port>/
    e.g. 192.168.1.1:60100/

Logs for container, most recent at top of page, use re-load to refresh

    <your_host>:<your_port>/logs/<container_name_or_id>
    e.g. http://192.168.1.1:60100/logs/some-rabbit_1

Raw log listing for container, most recent last

    <your_host>:<your_port>/raw/<container_name_or_id>
    e.g. http://192.168.1.1:60100/raw/some-rabbit_1

Build (in the `dlogs` repo. folder)

    docker build -t dlogs .

Run - select any number to replace `60100`

    docker run -d -p 60100:5000 \
        -v /var/run/docker.sock:/var/run/docker.sock \
        --name dlogs dlogs

Shutdown

    docker rm -f dlogs
