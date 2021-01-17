#!/usr/bin/env python
import argparse

from u3n.server import HttpServer

parser = argparse.ArgumentParser()
parser.add_argument("--host", dest="host", type=str, default="127.0.0.1")
parser.add_argument("--port", dest="port", type=int, default=8000)
args = parser.parse_args()
config = vars(args)

HttpServer(**config).run()
