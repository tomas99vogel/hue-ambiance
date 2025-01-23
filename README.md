# hue-ambiance

This Python script syncs the color and brightness of Philips Hue light(s) with what's happening on your screen, turning into into nice ambiance decoration. 
🔴🟢🔵

## Function
The script captures a portion of the screen (or full screen, if needed, although not recommended at higher resolutions) and extracts the most dominant colors.
It then converts these colors into values compatible with the Philips Hue API (Hue, Saturation, and Brightness) and syns the color via Hue API in real time. 
To make the lights pop a bit more, it skews the color to a more vibrant, saturated version.

## Usage
```
pip install -r requirements
```
```
python sync_lights.py
```

## Misc
Just a project for fun.

TBD:
- Tune the correct color matching
- Refactor the code to support more light and properly allocate the color complementary composition
- Create option to assign the light to a side of a screen a capture dominant color only from that region
- Add support for Effects, not just colors
