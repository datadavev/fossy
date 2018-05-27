'''
Control a FOSSCAM camera.

commands:

  list: list the cameras in configuration
  presets: list the PTZ presets
  goto: got to a named preset
  snapshot: get an image from the camera
  capture: get an image for each direction listed in the capture field of config
'''

import sys
import os
import argparse
import logging
import yaml
from datetime import datetime
import time
from . import *

def doCapture(camera, direction, fn_dest):
  logging.info("Capture %s to %s", direction, fn_dest)
  camera.setSnapConfig(quality=FosscamCamera.QUALITY_HIGH)
  time.sleep(1)
  camera.gotoPTZPoint(direction)
  time.sleep(5)
  camera.getStaticImage(fn_dest)


def doCaptures(camera, config):
  base_path = os.path.expanduser(config["capture"]["base_path"])
  tnow = datetime.now()
  for action in config["capture"]["actions"]:
    action_path = tnow.strftime(action["path"])
    action_path = os.path.join(base_path, action_path)
    try:
      os.makedirs( action_path, 0o775 )
    except FileExistsError as e:
      pass
    fn_dest = datetime.now().strftime(action["name"])
    fn_dest = os.path.join(action_path, fn_dest)
    doCapture(camera, action["direction"], fn_dest)


def main():
  parser = argparse.ArgumentParser(description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('-l', '--log_level',
                      action='count',
                      default=0,
                      help='Set logging level, multiples for more detailed.')
  parser.add_argument('--config',
                      default=os.path.expanduser("~/.config/fossy/fossy.yaml"),
                      help="Path to configuration file")
  parser.add_argument('-c','--camera',
                      default=None,
                      help="Name of camera")
  parser.add_argument('-n','--name',
                      help="Name parameter for request",
                      default=None)
  parser.add_argument('command',
                      nargs='?',
                      default="list",
                      help='Command to invoke')
  args = parser.parse_args()
  # Setup logging verbosity
  levels = [logging.WARNING, logging.INFO, logging.DEBUG]
  level = levels[min(len(levels) - 1, args.log_level)]
  logging.basicConfig(level=level,
                      format="%(asctime)s %(levelname)s %(message)s")
  config = {}
  with open(args.config, "r") as config_data:
    config = yaml.load(config_data)
  logging.debug(str(config))
  command = args.command
  if args.camera is None:
    command= "list"
  if args.command == 'list':
    print("Cameras registered:")
    for camera in config['cameras']:
      print(camera)
    return 0
  camera = FosscamCamera(config['cameras'][args.camera])
  if args.command == 'presets':
    print("\n".join(camera.listPTZpoints()))
    return 0
  if args.command == "goto":
    print(camera.gotoPTZPoint(args.name))
    return 0
  if args.command == "snapshot":
    res = camera.setSnapConfig(quality=FosscamCamera.QUALITY_HIGH)
    print(res)
    dest_fn = args.name
    if dest_fn is None:
      dest_fn = "{}_{}.jpg".format(datetime.now().strftime("%Y%m%dT%H%M%S"), args.camera)
    res = camera.getStaticImage(dest_fn)
    return 0
  if args.command == "capture":
    doCaptures(camera, config)


if __name__ == "__main__":
  sys.exit(main())