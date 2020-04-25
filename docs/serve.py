#!/usr/bin/env python
from subprocess import call

# initial make
call(["python", "-m", "sphinx", ".", "/tmp/_build"])
from livereload import Server, shell

server = Server()
server.watch("..", shell("python -m sphinx . /tmp/_build"))
server.serve(root="/tmp/_build/", liveport=35730, port=8001, host="0.0.0.0")
