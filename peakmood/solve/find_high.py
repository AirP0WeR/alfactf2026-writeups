from PIL import Image
import sys

img = Image.open("../artifacts/apktool_out/res/raw/global_relief.jpg")
print("size", img.size, "mode", img.mode)

# Convert to L (grayscale) — though it might already be L or RGB. Bitmap.getPixel(x,y) & 0xFF takes blue channel
# In jadx code: getPixel & 255 → low byte (blue in ARGB)
import struct
W, H = img.size
assert (W, H) == (2880, 1440), (W, H)

# Sample blue channel; based on code lerp uses & 255
if img.mode != "RGB" and img.mode != "L":
    img = img.convert("RGB")

# step = 81063 mm/step; zero=128
# elevation_m = round((value - 128) * 81.063)
threshold_m = 9400
print("Looking for pixels yielding elevation >= ", threshold_m)

# value such that (v - 128) * 81.063 >= 9400 → v >= 128 + 116 = 244
target_v = int(128 + (threshold_m / 81.063))
print("target value >=", target_v)

count = 0
samples = []
for y in range(H):
    for x in range(W):
        if img.mode == "RGB":
            r, g, b = img.getpixel((x, y))
            v = b
        else:
            v = img.getpixel((x, y))
        if v >= target_v:
            count += 1
            if len(samples) < 30:
                # convert pixel to lat/lon
                lon = (x / 2880.0) * 360.0 - 180.0
                lat = 90.0 - (y / 1439.0) * 180.0
                # Estimate elevation using lerp at center; but for sample, use direct
                elev_m = round((v - 128) * 81.063)
                samples.append((x, y, lat, lon, v, elev_m))

print("count=", count)
for s in samples:
    print(s)
