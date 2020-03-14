#! /usr/bin/env python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import logging

import sys
def setup_custom_logger(name):
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    handler = logging.FileHandler('voicelog.txt', mode='w')
    handler.setFormatter(formatter)
    screen_handler = logging.StreamHandler(stream=sys.stdout)
    screen_handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.addHandler(screen_handler)
    return logger

logger = setup_custom_logger('voiceKB')


import dbus
import evdev
import keymap
from time import sleep

HID_DBUS = 'org.yaptb.btkbservice'
HID_SRVC = '/org/yaptb/btkbservice'

import argparse
import model
import numpy as np

kb = 'test holder val'

from collections import deque
#remember the last 5 commands
key_memory_list = ["","","","",""]
dKeyMem = deque(key_memory_list)
#keep track if its listening
isListening = True


voice_to_keys = {
  "go_forwards": 40,
  "go_backwards": 41,
  "move_down": 81,
  "go_down": 81,
  "go_left": 80,
  "move_left": 80,
  "move_right": 79,
  "go_right": 79,
  "move_up": 82,
  "go_up": 82,
  "home phrase": 74, # need to train it to have a home phrase
  "begin_application": 8888,
  "begin_program": 8888,
  "begin_task": 8888,
  "start_application": 8888,
  "start_game": 8888,
  "start_program": 8888,
  "start_task": 8888,
  "close_application": 9999,
  "close_program": 9999,
  "close_task": 9999,
  "stop_application": 9999,
  "stop_program": 9999,
  "stop_task": 9999
}

def print_results(result, commands, labels, top=3):
  """Example callback function that prints the passed detections."""
  global isListening #use the global one as we're assigning in this function too.
  top_results = np.argsort(-result)[:top]
  dKeyMem.pop() #pop(delete) the oldest one
  dKeyMem.appendleft(labels[top_results[0]]) #add the latest top detection to the list
  print('adding this to list: ' + labels[top_results[0]])
  #print(dKeyMem)

  for p in range(top):
    l = labels[top_results[p]]
    if l in commands.keys():
      threshold = commands[labels[top_results[p]]]["conf"]
    else:
      threshold = 0.5
    if top_results[p] and result[top_results[p]] > threshold:
      sys.stdout.write("\033[1m\033[93m*%15s*\033[0m (%.3f)" %
                       (l, result[top_results[p]]))
      try:
        keyvalue = voice_to_keys[l]
      except:
        print("unrecognized value for the keys we're interested in")
        keyvalue = 0 # just zero it out if it's not one of the onese we're looking for
      if l == dKeyMem[1]:
        print('likely dupe as looks like ' + dKeyMem[1] )
      else:
        if keyvalue == 8888: #hacky code magic numbers
          isListening = True
          print("Now Listening")
          logger.info("Started listening")
        if keyvalue == 9999: #TODO fix this
          isListening = False
          print("Not Listening!")
          logger.info("Stopped listening")
        if keyvalue < 8888:  #TODO fix this
          if isListening:
            logger.info("Sending key " + l)
            kb.btk_service.send_keys([161, 1, 0, 0, 0, 0, 0, 0, 0, 0])
            kb.btk_service.send_keys([161, 1, 0, 0, keyvalue, 0, 0, 0, 0, 0])
            kb.btk_service.send_keys([161, 1, 0, 0, 0, 0, 0, 0, 0, 0])
          else:
            print("not listening")
            logger.info("Would have Sent key " + l)
    elif result[top_results[p]] > 0.005:
      sys.stdout.write(" %15s (%.3f)" % (l, result[top_results[p]]))
  sys.stdout.write("\n")


def main():
  isListening = True
  while True:
    try:
      parser = argparse.ArgumentParser()
      model.add_model_flags(parser)
      args = parser.parse_args()
      interpreter = model.make_interpreter(args.model_file)
      interpreter.allocate_tensors()
      mic = args.mic if args.mic is None else int(args.mic)
      model.classify_audio(mic, interpreter,
                       labels_file="config/labels_gc2.raw.txt",
                       result_callback=print_results,
                       sample_rate_hz=int(args.sample_rate_hz),
                       num_frames_hop=int(args.num_frames_hop))
    except:
      logger.error("crashed and restarting the model: " + str(sys.exc_info()[0]))
      sys.stdout.write("Crashed so trying to restart")
      sys.stdout.write("print Unexpected error" + str(sys.exc_info()[0]))


class Kbrd:
    """
    Take the events from a physically attached keyboard and send the
    HID messages to the keyboard D-Bus server.
    """
    def __init__(self):
        self.target_length = 6
        self.mod_keys = 0b00000000
        self.pressed_keys = []
        self.have_kb = False
        self.dev = None
        self.bus = dbus.SystemBus()
        self.btkobject = self.bus.get_object(HID_DBUS,
                                             HID_SRVC)
        self.btk_service = dbus.Interface(self.btkobject,
                                          HID_DBUS)
        #self.wait_for_keyboard()
        print("Not linking to physical keyboard so skipping wait_for_keyboard()")

    def wait_for_keyboard(self, event_id=0):
        """
        Connect to the input event file for the keyboard.
        Can take a parameter of an integer that gets appended to the end of
        /dev/input/event
        :param event_id: Optional parameter if the keyboard is not event0
        """
        while not self.have_kb:
            try:
                # try and get a keyboard - should always be event0 as
                # we're only plugging one thing in
                self.dev = evdev.InputDevice('/dev/input/event{}'.format(
                    event_id))
                self.have_kb = True
            except OSError:
                print('Keyboard not found, waiting 3 seconds and retrying')
                sleep(3)
            print('found a keyboard')

    def update_mod_keys(self, mod_key, value):
        """
        Which modifier keys are active is stored in an 8 bit number.
        Each bit represents a different key. This method takes which bit
        and its new value as input
        :param mod_key: The value of the bit to be updated with new value
        :param value: Binary 1 or 0 depending if pressed or released
        """
        self.mod_keys = value << mod_key

    def update_keys(self, norm_key, value):
        if value < 1:
            self.pressed_keys.remove(norm_key)
        elif norm_key not in self.pressed_keys:
            self.pressed_keys.insert(0, norm_key)
        len_delta = self.target_length - len(self.pressed_keys)
        if len_delta < 0:
            self.pressed_keys = self.pressed_keys[:len_delta]
        elif len_delta > 0:
            self.pressed_keys.extend([0] * len_delta)

    @property
    def state(self):
        """
        property with the HID message to send for the current keys pressed
        on the keyboards
        :return: bytes of HID message
        """
        return [0xA1, 0x01, self.mod_keys, 0, *self.pressed_keys]

    def send_keys(self):
        print('sending key' + str(len(self.pressed_keys)))
        self.btk_service.send_keys(self.state)

    def event_loop(self):
        """
        Loop to check for keyboard events and send HID message
        over D-Bus keyboard service when they happen
        """
        print('Listening...')
        for event in self.dev.read_loop():
            # only bother if we hit a key and its an up or down event
            if event.type == evdev.ecodes.EV_KEY and event.value < 2:
                key_str = evdev.ecodes.KEY[event.code]
                mod_key = keymap.modkey(key_str)
                if mod_key > -1:
                    self.update_mod_keys(mod_key, event.value)
                else:
                    self.update_keys(keymap.convert(key_str), event.value)
            self.send_keys()


if __name__ == '__main__':
    print('Setting up keyboard')
    kb = Kbrd()

    #print('starting event loop')
    #kb.event_loop()
    print('starting coral board to listen')
    main()

