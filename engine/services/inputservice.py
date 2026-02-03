
# input mapping service
# initialises with a mapping dict of
# key trigger -> "event" (arbitrary string)
# i.e. K_up
import sys
from pathlib import Path
from typing import Callable

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pygame
import pygame.locals as pl
import pygame._sdl2.controller as ctrl

KEY_VALUE_TO_NAME = {
    value: name
    for name, value in vars(pl).items()
    if name.startswith("K_")
}

BUTTON_VALUE_TO_NAME = {
    value: name
    for name, value in vars(pl).items()
    if name.startswith("CONTROLLER_BUTTON_")
}

MOUSE_VALUE_TO_NAME = {
    1: "MOUSE_LEFT",
    2: "MOUSE_MIDDLE",
    3: "MOUSE_RIGHT",
    4: "MOUSE_SCROLL_UP",
    5: "MOUSE_SCROLL_DOWN"
}


EVENT_TYPES_LISTENING = {
    pygame.KEYDOWN: "key",
    pygame.KEYUP: "key",
    pygame.CONTROLLERBUTTONDOWN: "button",
    pygame.CONTROLLERBUTTONUP: "button",
    pygame.MOUSEBUTTONDOWN: "mouse",
    pygame.MOUSEBUTTONUP: "mouse",
}

if __name__ == "__main__":
    with open("validevents.txt", "w") as f:
        f.write("=== KEY EVENTS ===\n")
        for item in KEY_VALUE_TO_NAME.values():
            f.write(f"{item}\n")
        f.write("=== BUTTON EVENTS ===\n")
        for item in BUTTON_VALUE_TO_NAME.values():
            f.write(f"{item}\n")
        f.write("=== KEY EVENTS ===\n")
        for item in MOUSE_VALUE_TO_NAME.values():
            f.write(f"{item}\n")

class Criteria():
    @staticmethod
    def on_press(f):
        return True if f==1 else False
    
    @staticmethod
    def on_held(f):
        return True if f>0 else False
    
    @staticmethod
    def on_release(f):
        return True if f==-1 else False
    
    @staticmethod
    def make_on_held_interval(x):
        def on_held_interval(f):
            return True if f % x == 0 else False
        return on_held_interval

class Event():
    def __init__(self, triggers: str | list, criteria: Callable, callback: Callable, args: list):
        self.triggers = triggers if isinstance(triggers, list) else [triggers]
        self.criteria = criteria
        self.callback = callback
        self.args = args


class InputService():
    def __init__(self):
        self.gamepad = None
        self.input_roster = {}
        self.events = []
        try:
            ctrl.init()
        except Exception:
            pass
        for item in KEY_VALUE_TO_NAME.values():
            self.input_roster[item] = 0
        for item in BUTTON_VALUE_TO_NAME.values():
            self.input_roster[item] = 0
        for item in MOUSE_VALUE_TO_NAME.values():
            self.input_roster[item] = 0

    def register_event(self, event: Event):
        self.events.append(event)

    def check_events(self):
        for trigger, frames in self.input_roster.items():
            if frames == 0:
                continue
            for event in self.events:
                if trigger not in event.triggers:
                    continue
                if event.criteria(frames):
                    event.callback(frames, *event.args)


    def controllercheck(self):
        try:
            count = ctrl.get_count()
        except pygame.error:
            count = 0

        if count > 0 and self.gamepad is None:
            try:
                self.gamepad = ctrl.Controller(0)
            except Exception:
                self.gamepad = None
        elif count == 0:
            self.gamepad = None

    def tick(self, events):
        self.controllercheck()
        self.process_events(events)
        self.check_events()
        for item in self.input_roster:

            if self.input_roster[item] == 0:    # never pressed
                continue
            if self.input_roster[item] > 0:     # positive / pressed
                self.input_roster[item] += 1
            elif self.input_roster[item] < 0:   # negative / unpressed after first press
                self.input_roster[item] -= 1


    def process_events(self, events):
        for event in events:
            event_type = event.type
            if not event_type in EVENT_TYPES_LISTENING.keys():
                continue
            target = EVENT_TYPES_LISTENING[event.type]
            value = getattr(event, target, None)
            if target == "key":
                name = KEY_VALUE_TO_NAME.get(value, "unknown")
            elif target == "button":
                name = BUTTON_VALUE_TO_NAME.get(value, "unknown")
            elif target == "mouse":
                name = MOUSE_VALUE_TO_NAME.get(value, "unknown")
            else:
                name = "unknown"
            updown = -1 if event_type in [pygame.KEYUP, pygame.CONTROLLERBUTTONUP, pygame.MOUSEBUTTONUP] else 1
            self.input_roster[name] = updown
        


def controllertest():
    ctrl.init()
    from engine.debug.textwindow import TextWindow

    tw = TextWindow(width=60, height=25)
    em = InputService()

    while tw.running:
        tw.tick()
        em.tick(tw.events)
        tw.blank()
        
        tw.write(2, 1, f"CONTROLLER BUTTON TEST")
        tw.write(2, 2, f"FPS: {tw.clock.get_fps():.2f}")
        
        y = 4
        tw.write(2, y, "CONTROLLER BUTTONS:")
        y += 1
        
        for name, value in em.input_roster.items():
            if not name.startswith("CONTROLLER_BUTTON_"):
                continue
            button_name = name.replace("CONTROLLER_BUTTON_", "")
            tw.write(3, y, button_name)
            
            if value > 0:
                tw.write(20, y, "[PRESSED]")
                tw.write(40, y, f"{str(abs(value))} frames")
            elif value < 0:
                tw.write(20, y, "[released]")
                tw.write(40, y, f"{str(abs(value))} frames")
            else:
                tw.write(20, y, "[neutral]")
                tw.write(40, y, "0")
            
            y += 1
        tw.clock.tick(120)

if __name__ == "__main__":
    controllertest()

