import pygame
import os
import pygameui as ui

from qhue import Bridge, QhueException, create_new_username
from time import sleep

# Note: must make credential file with bridge IP address to run
with open("bridge.conf", "r") as bridge_file:
    BRIDGE_IP = bridge_file.readlines()[0]

CRED_FILE_PATH = "qhue_username.txt"

MARGIN = 10
BUTTON_WIDTH = 110
BUTTON_HEIGHT = 60


def get_bridge():
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

def launch_app():
    b = get_bridge()
    lights = b.lights


class LightswitchScene(ui.Scene):
    def __init__(self):
        ui.Scene.__init__(self)

        label_height = ui.theme.current.label_height
        scrollbar_size = ui.SCROLLBAR_SIZE

        # Light Color Buttons
        self.day_button = ui.Button(ui.Rect(
            MARGIN, 88, BUTTON_WIDTH, BUTTON_HEIGHT), 'Day')
        self.day_button.on_clicked.connect(self.day)
        self.add_child(self.day_button)

        self.night_button = ui.Button(ui.Rect(
            (MARGIN) + 120, 88,
            BUTTON_WIDTH, BUTTON_HEIGHT), 'Night')
        self.night_button.on_clicked.connect(self.night)
        self.add_child(self.night_button)

        self.theater_button = ui.Button(ui.Rect(
            MARGIN, (MARGIN) + 60 + 88,
            BUTTON_WIDTH, BUTTON_HEIGHT), 'Theater')
        self.theater_button.on_clicked.connect(self.theater)
        self.add_child(self.theater_button)

        self.chill_button = ui.Button(ui.Rect(
            (MARGIN) + 120, (MARGIN) + 60 + 88,
            BUTTON_WIDTH, BUTTON_HEIGHT), 'Chill')
        self.chill_button.on_clicked.connect(self.chill)
        self.add_child(self.chill_button)

        # Power Button
        self.power_button = ui.Button(ui.Rect(
            MARGIN, MARGIN, 80, 60), 'Power')
        self.power_button.on_clicked.connect(self.power)
        self.add_child(self.power_button)

        # Brightness Slider
        self.brightness_slider = ui.SliderView(ui.Rect(
            275, MARGIN, scrollbar_size, 220),
            ui.VERTICAL, 0, 100)
        self.brightness_slider.on_value_changed.connect(self.change_brightness)
        self.add_child(self.brightness_slider)

        # Light Enabled Checkboxes
        self.enabled_box = ui.Checkbox(ui.Rect(self.power_button.frame.right + 20,
            3 * MARGIN, 20, 100), "1")
        self.add_child(self.enabled_box)

        self.enabled1_box = ui.Checkbox(ui.Rect(self.enabled_box.frame.right + 35,
            3 * MARGIN, 20, 100), "2")
        self.add_child(self.enabled1_box)

        self.enabled2_box = ui.Checkbox(ui.Rect(self.enabled1_box.frame.right + 35,
            3 * MARGIN, 20, 100), "3")
        self.add_child(self.enabled2_box)

    def layout(self):
        ui.Scene.layout(self)

    def day(self, btn, mbtn):
        print("this is day")

    def night(self, btn, mbtn):
        print("this is night")
    
    def theater(self, btn, mbtn):
        print("this is theater")

    def chill(self, btn, mbtn):
        print("this is chill")

    def power(self, btn, mbtn):
        print("time 2 sleep")

    def change_brightness(self, slider_view, value):
        print("new slider val: {}".format(value))


if __name__ == "__main__":
    os.putenv('SDL_FBDEV', '/dev/fb1')
    os.putenv('SDL_MOUSEDRV', 'TSLIB')
    os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')

    ui.init("Lightswitch", (320,240))
    pygame.mouse.set_visible(False)
    ui.scene.push(LightswitchScene())
    ui.run()

