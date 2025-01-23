from config import KEY, BRIDGE_IP
import requests
from mss import mss
from PIL import Image
import numpy as np
from threading import Thread
from time import sleep

MAX_BRIGHTNESS = 255
MAX_SATURATION = 255
MAX_HUE = 65535

LIGHT_ID = [3,4] 

def rgb_to_xy(r, g, b):
    """
    Converts RGB to CIE 1931 xy
    """
    r, g, b = [x / 255 for x in (r, g, b)]
    r = (r / 12.92 if r <= 0.04045 else ((r + 0.055) / 1.055) ** 2.4)
    g = (g / 12.92 if g <= 0.04045 else ((g + 0.055) / 1.055) ** 2.4)
    b = (b / 12.92 if b <= 0.04045 else ((b + 0.055) / 1.055) ** 2.4)

    X = r * 0.4124 + g * 0.3576 + b * 0.1805
    Y = r * 0.2126 + g * 0.7152 + b * 0.0722
    Z = r * 0.0193 + g * 0.1192 + b * 0.9505

    x = X / (X + Y + Z) if (X + Y + Z) != 0 else 0
    y = Y / (X + Y + Z) if (X + Y + Z) != 0 else 0

    # Increase saturation 
    center_x, center_y = 0.33, 0.33
    dx, dy = x - center_x, y - center_y
    distance = (dx ** 2 + dy ** 2) ** 0.5
    
    if distance > 0:
        dx, dy = dx / distance, dy / distance
        x_new = center_x + dx * distance * 2
        y_new = center_y + dy * distance * 2
        
        x_new = max(0, min(x_new, 1))
        y_new = max(0, min(y_new, 1))
        
        return x_new, y_new
    else:
        return x, y

class GamingAmbiance:
    def __init__(self, region=None, update_interval=0.5):
        """
        Initialize the ambiance updater.

        :param region: Tuple (left, top, width, height) for screen capture area.
                       If None, captures the entire screen.
        :param update_interval: Time (in seconds) between updates.
        """
        self.region = region
        self.update_interval = update_interval
        self.running = False
        self.dominant_colors = [(0, 0, 0), (0, 0, 0)]



    def _capture_screen(self):
        with mss() as sct:
            while self.running:
                # Define the screen capture region, defaul = whoel screen
                monitor = sct.monitors[1] 
                if self.region:
                    monitor = {
                        "left": self.region[0],
                        "top": self.region[1],
                        "width": self.region[2],
                        "height": self.region[3]
                    }

                # Capture the screen and downscale 32*18 pixels. Full screenshot is too large and reduces performance.
                screenshot = sct.grab(monitor)
                img = Image.frombytes("RGB", screenshot.size, screenshot.rgb).resize(
                    (32, 18), Image.Resampling.LANCZOS
                )

                pixels = np.array(img.getdata())
                color_1 = tuple(map(int, np.mean(pixels[:len(pixels)//2], axis=0)))
                color_2 = tuple(map(int, np.mean(pixels[len(pixels)//2:], axis=0)))

                self.dominant_colors = [color_1, color_2]

                sleep(self.update_interval)

    def start(self):
        self.running = True
        Thread(target=self._capture_screen, daemon=True).start()

    def stop(self):
        """Stop the ambiance updater and turn off the lights."""
        self.running = False
        update_hue_light((0,0,0),3,False)
        update_hue_light((0,0,0),4,False)

    def get_colors(self):
        return self.dominant_colors

def update_hue_light(color, light_id, switch=True):
    url = f"http://{BRIDGE_IP}/api/{KEY}/lights/{light_id}/state"
    x, y = rgb_to_xy(*color)
    brightness = max(*color)
    brightness = int((brightness / 255) * 254) 
    payload = {
        "on": switch,
        "xy": [x, y],
        "bri": brightness
    }
    requests.put(url, json=payload)


if __name__ == "__main__":
    region = None #(500, 300, 800, 450)  
    ambiance = GamingAmbiance(region=region, update_interval=0.5)
    
    ambiance.start()
    try:
        while True:
            colors = ambiance.get_colors()
            for color,id in zip(colors,LIGHT_ID):
                update_hue_light(color, id)

    except KeyboardInterrupt:
        ambiance.stop()