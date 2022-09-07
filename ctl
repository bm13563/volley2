#!/bin/bash

case $1 in
    init)
        sudo chmod 666 /var/run/docker.sock
        docker pull postgres
    ;;
    build)
        source venv/bin/activate
        sudo chmod 666 /var/run/docker.sock
        pip freeze --exclude-editable > requirements.txt
        docker build -t volley2 .
    ;;
    start)
        docker run -it --name volley2-postgres --rm -p 5432:5432 -e POSTGRES_USER=volley -e POSTGRES_PASSWORD=volley -d postgres >/dev/null 2>&1
        docker run -it --name volley2 --rm --volume "$(pwd)"/api:/volley2/api --net=host --env-file ./dev.env volley2:latest
    ;;
    stop)
        docker stop volley2-postgres
        docker rm volley2-postgres
    ;;
    reset)
        docker stop volley2-postgres >/dev/null 2>&1
        docker rm volley2-postgres >/dev/null 2>&1
        docker run -it --name volley2-postgres --rm -p 5432:5432 -e POSTGRES_USER=volley -e POSTGRES_PASSWORD=volley -d postgres >/dev/null 2>&1
    ;;
    shell)
        docker run -it --name volley2 --rm --volume "$(pwd)"/api:/volley2/api --net=host --env-file ./dev.env volley2:latest sh
    ;;
esac