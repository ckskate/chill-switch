import pygame
import os
import pygameui as ui
import math

from qhue import Bridge, QhueException, create_new_username
from time import sleep

# Note: must make credential file with bridge IP address to run
with open("bridge.conf", "r") as bridge_file:
    BRIDGE_IP = bridge_file.read()

CRED_FILE_PATH = "qhue_username.txt"

MARGIN = 10

BUTTON_WIDTH = 110
BUTTON_HEIGHT = 60

SLIDER_HEIGHT = 125

BRIGHTNESS_FACTOR = 255 // 4

SCENES = {
    "day": {
        "bri": 255,
        "power_list": [True, True, True],
        "color_list": [[0.3128, 0.3290]],
        "colormode": "xy"
    },
    "night": {
        "bri": 175,
        "power_list": [True, True, True],
        "color_list": [[0.4476, 0.4075]],
        "colormode": "xy"
    },
    "theater": {
        "bri": 255 // 3,
        "power_list": [False, True, False]
    },
    "chill": {
        "bri": 100,
        "power_list": [True, True, True]
    }
}


class Hue:
    def __init__(self):
        self.bridge = self.get_bridge()

    def get_bridge(self):
        if not os.path.exists(CRED_FILE_PATH):
            while True:
                try:
                    username = create_new_username(BRIDGE_IP)
                    break
                except QhueException as err:
                    print("Error occurred while creating new user: {}".format(err))
                    return

            with open(CRED_FILE_PATH, "w") as cred_file:
                cred_file.write(username)

        else:
            with open(CRED_FILE_PATH, "r") as cred_file:
                username = cred_file.read()

        bridge = Bridge(BRIDGE_IP, username)
        return bridge

    def get_bri(self):
        light_list = self.light_list()
        avg = 0 
        count = self.light_power_states().count(True)
        if count == 0:
            return avg

        for light in light_list:
            if light['state']['on'] == True:
                avg += light['state']['bri']
        print("bri: {}".format(avg//count))
        return avg // count

    def light_list(self):
        lights = self.bridge.lights()
        return [lights[key] for key in sorted(lights.keys())]

    def light_power_states(self):
        light_states = []
        for light in self.light_list():
            light_states.append(light['state']['on'])
        return light_states

    def toggle_power(self, only_one=None, to_value=False):
        light_states = self.light_power_states()

        if only_one != None:
            self.bridge.lights(only_one+1, 'state', on=to_value)
            return

        if light_states.count(True) >= len(light_states) // 2:
            for i in xrange(len(light_states)):
                self.bridge.lights(i+1, 'state', on=to_value)
        else:
            for i in xrange(len(light_states)):
                self.bridge.lights(i+1, 'state', on=to_value)

    def set_brightness(self, val, set_all=False):
        val = int(math.ceil(val))
        if val >= 255: val = 255
        elif val < 0: val = 0

        light_states = self.light_power_states()
         
        for i in xrange(len(light_states)):
            if light_states[i] == True:
                self.bridge.lights(i+1, 'state', bri=val)
            elif set_all == True:
                self.bridge.lights(i+1, 'state', on=True, bri=val)

    def set_color(self, light_index, val_type, val, set_all=False):
        if not set_all:
            if val_type == "xy":
                self.bridge.lights(i+1, 'state', on=True, xy=val)  
            elif val_type == "hsl":
                self.bridge.lights(i+1, 'state', on=True, hsl=val)
            elif val_type == "ct":
                self.bridge.lights(i+1, 'state', on=True, ct=val) 
        else:
            for i in xrange(3):
                if val_type == "xy":
                    self.bridge.lights(i+1, 'state', on=True, xy=val)  
                elif val_type == "hsl":
                    self.bridge.lights(i+1, 'state', on=True, hsl=val)
                elif val_type == "ct":
                    self.bridge.lights(i+1, 'state', on=True, ct=val) 


class Switch:
    def __init__(self, ui):
        self.ui = ui
        self.hue = Hue()

    def initialize_checkboxes(self):
        checkbox_statuses = self.hue.light_power_states()
        for i, box in enumerate(self.ui.checkboxes):
            if checkbox_statuses[i]:
                box.toggle()

    def toggle_checkboxes(self):
        light_states = self.hue.light_power_states()
        for i, box in enumerate(self.ui.checkboxes):
            if box.state != light_states[i]:
                box.toggle()

    def toggle_power(self):
        light_states = self.hue.light_power_states()
        toggle_val = (light_states.count("False") > 0)
        self.hue.toggle_power(to_value=toggle_val)
        self.toggle_checkboxes()

    def brightness_up(self, btn, mbtn):
        new_bri = self.hue.get_bri() + BRIGHTNESS_FACTOR

        # turn on all the lights if bri+ touched while all are off
        power_states = self.hue.light_power_states()
        if power_states.count(False) == len(power_states):
            self.toggle_power()

        self.hue.set_brightness(new_bri)

    def brightness_down(self, btn, mbtn):
        new_bri = self.hue.get_bri() - BRIGHTNESS_FACTOR
        self.hue.set_brightness(new_bri)

    def toggle_light0(self):
        to_value = self.ui.checkboxes[0].checked
        self.hue.toggle_power(only_one=0, to_value=to_value)

    def toggle_light1(self):
        to_value = self.ui.checkboxes[1].checked
        self.hue.toggle_power(only_one=1, to_value=to_value)

    def toggle_light2(self):
        to_value = self.ui.checkboxes[2].checked
        self.hue.toggle_power(only_one=2, to_value=to_value)

    def set_scene(self, scene_name):
        scene = SCENES[scene_name]
        if not scene: return

        if "power_list" in scene.keys():
            for i in xrange(len(scene["power_list"])):
                self.hue.toggle_power(only_one=i, to_value=scene["power_list"][i])
            self.toggle_checkboxes()
        if "bri" in scene.keys():
            self.hue.set_brightness(scene["bri"])
        if "color_list" in scene.keys():
            if len(scene["color_list"]) == 1:
                self.hue.set_color(0, scene["colormode"], scene["color_list"][0],
                                   set_all=True)
            else:
                for i, color in enumerate(scene["color_list"]):
                    self.hue.set_color(i+1, scene["colormode"], color)

    def day(self, btn, mbtn):
        self.set_scene("day")
        print("this is day")

    def night(self, btn, mbtn):
        self.set_scene("night")
        print("this is night")
    
    def theater(self, btn, mbtn):
        self.set_scene("theater")
        print("this is theater")

    def chill(self, btn, mbtn):
        self.set_scene("chill")
        print("this is chill")

    def power(self, btn, mbtn):
        self.toggle_power()


class SwitchUI(ui.Scene):
    def __init__(self):
        ui.Scene.__init__(self)

        label_height = ui.theme.current.label_height
        scrollbar_size = ui.SCROLLBAR_SIZE

        self.switch = Switch(self)

        # Light Color Buttons
        self.day_button = ui.Button(ui.Rect(
            MARGIN, 88, BUTTON_WIDTH, BUTTON_HEIGHT), 'Day')
        self.day_button.on_clicked.connect(self.switch.day)
        self.add_child(self.day_button)

        self.night_button = ui.Button(ui.Rect(
            (MARGIN) + 120, 88,
            BUTTON_WIDTH, BUTTON_HEIGHT), 'Night')
        self.night_button.on_clicked.connect(self.switch.night)
        self.add_child(self.night_button)

        self.theater_button = ui.Button(ui.Rect(
            MARGIN, (MARGIN) + 60 + 88,
            BUTTON_WIDTH, BUTTON_HEIGHT), 'Theater')
        self.theater_button.on_clicked.connect(self.switch.theater)
        self.add_child(self.theater_button)

        self.chill_button = ui.Button(ui.Rect(
            (MARGIN) + 120, (MARGIN) + 60 + 88,
            BUTTON_WIDTH, BUTTON_HEIGHT), 'Chill')
        self.chill_button.on_clicked.connect(self.switch.chill)
        self.add_child(self.chill_button)

        # Power Button
        self.power_button = ui.Button(ui.Rect(
            MARGIN, MARGIN, 80, 60), "Power")
        self.power_button.on_clicked.connect(self.switch.power)
        self.add_child(self.power_button)

        # Brightness Buttons
        self.brightness_up_button = ui.Button(ui.Rect(
            self.chill_button.frame.right + 2 * MARGIN,
            self.night_button.frame.top, BUTTON_HEIGHT,
            BUTTON_HEIGHT), '+')
        self.brightness_up_button.on_clicked.connect(self.switch.brightness_up)
        self.add_child(self.brightness_up_button)

        self.brightness_down_button = ui.Button(ui.Rect(
            self.chill_button.frame.right + 2 * MARGIN,
            self.chill_button.frame.top, BUTTON_HEIGHT,
            BUTTON_HEIGHT), '-')
        self.brightness_down_button.on_clicked.connect(self.switch.brightness_down)
        self.add_child(self.brightness_down_button)

        # Light Enabled Checkboxes
        self.enabled_box = ui.Checkbox(ui.Rect(self.power_button.frame.right + 15,
            3 * MARGIN, 20, 40), "1")
        self.add_child(self.enabled_box)
        self.enabled_box.on_checked.connect(self.switch.toggle_light0)
        self.enabled_box.on_unchecked.connect(self.switch.toggle_light0)
        self.enabled_box.stylize()

        self.enabled_box1 = ui.Checkbox(ui.Rect(self.enabled_box.frame.right + 15,
            3 * MARGIN, 20, 40), "2")
        self.add_child(self.enabled_box1)
        self.enabled_box1.on_checked.connect(self.switch.toggle_light1)
        self.enabled_box1.on_unchecked.connect(self.switch.toggle_light1)
        self.enabled_box1.stylize()

        self.enabled_box2 = ui.Checkbox(ui.Rect(self.enabled_box1.frame.right + 15,
            3 * MARGIN, 20, 40), "3")
        self.add_child(self.enabled_box2)
        self.enabled_box2.on_checked.connect(self.switch.toggle_light2)
        self.enabled_box2.on_unchecked.connect(self.switch.toggle_light2)
        self.enabled_box2.stylize()

        self.checkboxes = [self.enabled_box, self.enabled_box1, self.enabled_box2]
        self.switch.initialize_checkboxes()



if __name__ == "__main__":
    os.putenv('SDL_FBDEV', '/dev/fb1')
    os.putenv('SDL_MOUSEDRV', 'TSLIB')
    os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')

    ui.init("Lightswitch", (320,240))
    pygame.mouse.set_visible(False)
    ui.scene.push(SwitchUI())
    ui.run()

