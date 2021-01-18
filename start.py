#!/usr/bin/env python
import argparse
from pathlib import Path

from u3n.server import HttpServer

parser = argparse.ArgumentParser()
parser.add_argument("--host", dest="host", type=str, default="127.0.0.1")
parser.add_argument("--port", dest="port", type=int, default=8000)
parser.add_argument("--path", dest="chroot_path", type=Path, default=Path.cwd())
args = parser.parse_args()
config = vars(args)

# validate path
config["chroot_path"].resolve(strict=True)

HttpServer(**config).run()
