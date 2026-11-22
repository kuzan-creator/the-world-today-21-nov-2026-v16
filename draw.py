#!/usr/bin/env python3
"""The World Today — Saturday 21 November 2026, v16.
Revision of v15: hero pictures 1-3 drawn richer and more realistic
(summit hall + detailed globe, Riyadh skyline + interception bursts,
Andean ridges + cracked ground + dust), and the left list column
shortened so items 19/20 no longer run into the right column.
Render 2048 supersample, LANCZOS to 1024. Deterministic: sine-hash grain only."""
import math
from PIL import Image, ImageDraw, ImageFont

SS = 2
W = H = 2048
MX = 16
RED = (198, 32, 32)
CREAM = (250, 246, 238)
PAPER = (252, 250, 244)
SEA = (198, 226, 240)
LANDC = (188, 170, 128)
INK = (26, 24, 20)
NAVY = (16, 24, 52)
GREY = (110, 104, 92)
MUT = (90, 86, 76)

FB = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FS = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
BB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
BS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def SERIF_B(n):
    return ImageFont.truetype(FB, n * SS)


def SERIF(n):
    return ImageFont.truetype(FS, n * SS)


def SANS_B(n):
    return ImageFont.truetype(BB, n * SS)


def SANS(n):
    return ImageFont.truetype(BS, n * SS)


def vgrad(d, box, top, bot):
    x0, y0, x1, y1 = box
    for yy in range(y0, y1, 2 * SS):
        t = (yy - y0) / max(1, y1 - y0)
        c = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        d.rectangle([x0, yy, x1, yy + 2 * SS], fill=c)


def grain(img, amp=4):
    px = img.load()
    w, h = img.size
    for yy in range(0, h, 3):
        for xx in range(0, w, 3):
            n = int(amp * math.sin(xx * 12.9898 + yy * 78.233) * 43758.5453) % (2 * amp + 1) - amp
            r, g, b = px[xx, yy]
            px[xx, yy] = (max(0, min(255, r + n)), max(0, min(255, g + n)), max(0, min(255, b + n)))


def wrap(d, text, font, width):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if d.textlength(t, font=font) <= width:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def badge(d, x, y, text):
    w = d.textlength(text, font=SANS_B(9)) + 12 * SS
    d.rectangle([x + 200 - w, y, x + 200, y + 15 * SS], fill=RED)
    d.text((x + 200 - w + 6 * SS, y + 2 * SS), text, font=SANS_B(9),
           fill=(255, 255, 255))


# Real continents, Natural Earth 110m land, Douglas-Peucker simplified (tol 1 deg).
CONTINENTS = [
((-45.2,-78.0),(-43.3,-80.0),(-54.2,-80.6),(-45.2,-78.0)),
((-121.2,-73.5),(-118.7,-73.5),(-122.6,-73.7),(-121.2,-73.5)),
((-125.6,-73.5),(-124.0,-73.9),(-127.3,-73.5),(-125.6,-73.5)),
((-99.0,-71.9),(-96.2,-72.5),(-102.3,-71.9),(-99.0,-71.9)),
((-68.5,-71.0),(-68.8,-72.2),(-75.0,-72.1),(-72.1,-71.2),(-71.2,-69.0),(-68.5,-71.0)),
((-58.6,-64.2),(-62.0,-64.8),(-65.7,-68.0),(-61.8,-70.7),(-60.8,-73.7),(-70.6,-76.6),(-77.2,-76.7),(-73.7,-77.9),(-78.0,-79.2),(-58.2,-83.2),(-28.5,-80.3),(-35.6,-79.5),(-35.8,-78.3),(-17.5,-75.1),(-15.4,-73.1),(-6.9,-70.9),(27.1,-70.5),(33.9,-68.5),(38.6,-69.8),(54.5,-65.8),(61.4,-68.0),(68.9,-67.9),(69.6,-69.7),(67.8,-70.3),(69.1,-70.7),(67.9,-71.9),(69.9,-72.3),(88.0,-66.2),(95.8,-67.4),(102.8,-65.6),(107.2,-67.0),(113.6,-65.9),(119.8,-67.3),(135.1,-65.3),(137.5,-67.0),(145.5,-66.9),(171.2,-71.7),(163.6,-76.2),(167.0,-78.8),(161.8,-79.2),(159.8,-80.9),(169.4,-83.8),(180,-84.7),(180,-90),(-180,-90),(-179.1,-84.1),(-143.1,-85.0),(-153.6,-83.7),(-152.9,-82.0),(-156.8,-81.1),(-146.4,-80.3),(-155.3,-79.1),(-158.4,-76.9),(-151.3,-77.4),(-135.2,-74.3),(-100.1,-74.9),(-103.7,-72.6),(-74.9,-73.9),(-67.4,-72.5),(-68.5,-69.7),(-67.3,-66.9),(-57.2,-63.5),(-58.6,-64.2)),
((-67.8,-53.9),(-65.0,-54.7),(-69.2,-55.5),(-74.7,-52.8),(-71.1,-54.1),(-68.6,-52.6),(-67.8,-53.9)),
((145.4,-40.8),(148.3,-40.9),(147.9,-43.2),(146.0,-43.5),(145.4,-40.8)),
((173.0,-40.9),(174.2,-41.3),(173.1,-43.9),(169.3,-46.6),(166.7,-46.2),(173.0,-40.9)),
((174.6,-36.2),(178.5,-37.7),(175.2,-41.7),(172.6,-34.5),(174.6,-36.2)),
((50.1,-13.6),(47.1,-24.9),(44.0,-25.0),(44.4,-16.2),(49.2,-12.0),(50.1,-13.6)),
((143.6,-13.8),(145.4,-15.0),(146.4,-19.0),(152.9,-25.3),(153.1,-30.9),(150.0,-37.4),(146.3,-39.0),(140.6,-38.0),(138.2,-34.4),(136.8,-35.3),(137.8,-32.9),(136.0,-34.9),(131.3,-31.5),(118.0,-35.1),(115.0,-34.2),(115.7,-31.6),(113.3,-26.1),(114.1,-21.8),(120.9,-19.7),(125.7,-14.2),(129.6,-15.0),(132.4,-11.1),(136.5,-11.9),(135.5,-15.0),(140.2,-17.7),(142.5,-10.7),(143.6,-13.8)),
((117.9,-8.1),(119.1,-8.7),(116.7,-9.0),(117.9,-8.1)),
((108.6,-6.8),(115.7,-8.4),(105.4,-6.9),(108.6,-6.8)),
((152.0,-5.5),(148.3,-5.7),(152.1,-4.1),(152.0,-5.5)),
((134.1,-1.2),(135.5,-3.4),(138.3,-1.7),(144.6,-3.9),(150.7,-10.6),(144.7,-7.6),(142.6,-9.3),(137.6,-8.4),(137.9,-5.4),(133.0,-4.1),(132.0,-2.8),(133.7,-2.2),(130.5,-0.9),(134.1,-1.2)),
((125.2,1.4),(120.2,0.2),(120.9,-1.4),(123.3,-0.6),(121.5,-1.9),(123.2,-5.3),(121.0,-2.6),(119.4,-5.4),(120.0,0.6),(125.2,1.4)),
((128.7,1.1),(128.1,-0.9),(127.9,2.2),(128.7,1.1)),
((105.8,-5.9),(102.6,-4.2),(95.3,5.5),(103.8,0.1),(106.1,-3.1),(105.8,-5.9)),
((117.9,1.8),(119.0,0.9),(116.1,-4.0),(110.2,-2.9),(109.1,-0.5),(109.7,2.0),(116.7,6.9),(119.2,5.4),(117.3,3.2),(117.9,1.8)),
((126.4,8.4),(125.4,5.6),(123.6,7.8),(121.9,7.2),(125.4,9.8),(126.4,8.4)),
((81.2,6.2),(79.9,6.8),(80.1,9.8),(81.2,6.2)),
((118.5,9.3),(117.2,8.4),(119.5,11.4),(118.5,9.3)),
((125.5,12.2),(124.8,10.1),(124.3,12.6),(125.5,12.2)),
((121.3,18.5),(122.5,17.1),(121.7,14.3),(124.1,12.5),(120.6,13.9),(119.9,16.4),(121.3,18.5)),
((-72.6,19.9),(-68.3,18.6),(-74.5,18.3),(-72.3,18.7),(-72.6,19.9)),
((110.3,18.7),(108.6,19.4),(110.8,20.1),(110.3,18.7)),
((-79.7,22.8),(-74.2,20.3),(-77.8,19.9),(-81.8,22.6),(-85.0,21.9),(-79.7,22.8)),
((121.2,22.8),(120.1,23.6),(121.5,25.3),(121.2,22.8)),
((15.5,38.2),(15.1,36.6),(12.4,37.6),(15.5,38.2)),
((141.0,37.1),(140.3,35.1),(135.8,33.5),(135.1,34.6),(131.0,33.9),(132.0,33.1),(130.2,31.4),(129.4,33.3),(135.7,35.5),(141.4,41.4),(141.0,37.1)),
((143.9,44.2),(145.5,43.3),(140.0,41.6),(142.0,45.6),(143.9,44.2)),
((-56.1,50.7),(-56.8,49.8),(-53.1,48.7),(-53.1,46.7),(-59.3,47.6),(-55.4,51.6),(-56.1,50.7)),
((143.6,50.7),(144.7,49.0),(143.2,49.3),(143.5,46.1),(142.1,46.0),(142.7,54.4),(143.6,50.7)),
((-6.8,52.3),(-10.0,51.8),(-9.7,53.9),(-6.7,55.2),(-5.7,54.6),(-6.8,52.3)),
((-153.0,57.1),(-154.7,57.5),(-152.1,57.6),(-153.0,57.1)),
((-3.0,58.6),(-4.1,57.6),(-2.0,57.7),(-3.1,56.0),(1.7,52.7),(1.4,51.3),(-5.2,50.0),(-3.4,51.4),(-5.3,52.0),(-4.6,53.5),(-2.9,54.0),(-6.1,56.8),(-5.0,58.6),(-3.0,58.6)),
((-85.2,65.7),(-80.1,63.7),(-87.2,63.5),(-85.2,65.7)),
((-14.5,66.5),(-13.6,65.1),(-18.7,63.5),(-24.3,65.6),(-14.5,66.5)),
((-75.9,67.1),(-77.2,67.6),(-75.1,68.0),(-75.9,67.1)),
((-175.0,66.6),(-169.9,66.0),(-173.0,64.3),(-178.7,66.1),(-180,65.0),(-180,69.0),(-175.0,66.6)),
((-178.7,70.9),(-180,71.5),(-177.6,71.3),(-178.7,70.9)),
((-90.5,69.5),(-87.4,67.2),(-85.5,69.9),(-82.6,69.7),(-81.3,67.6),(-85.8,66.6),(-93.2,62.0),(-94.7,58.9),(-92.3,57.1),(-82.3,55.1),(-79.9,51.2),(-78.6,52.6),(-79.8,54.7),(-76.5,56.5),(-78.5,58.8),(-77.3,59.9),(-78.1,62.3),(-73.8,62.4),(-69.6,61.1),(-67.6,58.2),(-64.6,60.3),(-61.8,56.3),(-57.3,54.6),(-55.7,52.1),(-60.0,50.2),(-66.4,50.2),(-71.1,46.8),(-65.1,49.2),(-64.5,46.2),(-60.5,47.0),(-59.8,45.9),(-65.4,43.5),(-66.2,44.5),(-64.4,45.3),(-70.1,43.7),(-70.0,41.6),(-74.0,40.8),(-75.9,37.2),(-76.3,39.2),(-75.7,35.6),(-81.3,31.4),(-80.4,25.2),(-84.1,30.1),(-93.2,29.8),(-96.6,28.3),(-97.9,22.4),(-96.3,19.3),(-94.4,18.1),(-89.6,21.3),(-86.8,21.3),(-88.9,15.9),(-83.1,15.0),(-83.9,11.4),(-82.2,9.0),(-76.8,8.6),(-71.8,12.4),(-71.7,9.1),(-69.9,12.2),(-68.2,10.6),(-61.9,10.7),(-58.5,6.8),(-51.3,4.2),(-50.4,-0.1),(-44.6,-2.7),(-40.0,-2.9),(-35.6,-5.1),(-34.7,-7.3),(-39.0,-13.8),(-40.9,-21.9),(-47.6,-24.9),(-53.8,-34.4),(-58.4,-33.9),(-56.8,-36.9),(-65.1,-41.1),(-63.5,-42.6),(-67.6,-46.3),(-66.0,-48.1),(-69.1,-50.7),(-68.2,-52.3),(-71.4,-53.9),(-74.9,-52.3),(-75.6,-48.7),(-74.1,-46.9),(-75.6,-46.6),(-72.7,-42.4),(-74.3,-43.2),(-70.2,-19.8),(-76.0,-14.6),(-81.2,-6.1),(-79.8,-2.7),(-80.9,-1.1),(-77.1,3.8),(-78.2,8.3),(-79.6,8.9),(-80.9,7.2),(-85.7,9.9),(-87.5,13.3),(-103.5,18.3),(-114.8,31.8),(-109.4,23.2),(-112.2,24.7),(-117.3,33.0),(-120.6,34.6),(-124.4,40.3),(-124.7,48.2),(-122.6,47.1),(-122.8,49.0),(-127.4,50.8),(-134.1,58.1),(-147.1,60.9),(-151.7,59.2),(-150.6,61.3),(-158.4,56.0),(-164.8,54.4),(-157.0,58.9),(-162.0,58.7),(-166.1,61.5),(-160.8,64.8),(-168.1,65.7),(-161.7,66.1),(-166.8,68.4),(-156.6,71.4),(-136.5,68.9),(-124.4,70.2),(-108.9,67.4),(-106.2,68.8),(-101.5,67.6),(-97.7,68.6),(-96.1,67.3),(-94.2,69.1),(-96.5,70.1),(-95.2,71.9),(-90.5,69.5)),
((-114.2,73.1),(-108.2,71.7),(-108.4,73.1),(-106.5,73.1),(-101.1,69.6),(-113.3,68.5),(-117.3,70.0),(-112.4,70.4),(-119.4,71.6),(-114.2,73.1)),
((-86.6,73.2),(-82.3,73.8),(-80.7,72.1),(-72.2,71.6),(-67.0,69.2),(-68.8,68.7),(-61.9,66.9),(-63.9,65.0),(-68.0,66.3),(-64.7,63.4),(-68.8,63.7),(-66.2,61.9),(-74.8,64.7),(-77.7,64.2),(-77.9,65.3),(-74.0,65.5),(-72.9,67.7),(-79.0,70.2),(-89.9,71.2),(-89.4,73.1),(-86.6,73.2)),
((-100.4,73.8),(-97.4,73.8),(-96.7,71.7),(-102.5,72.5),(-100.4,73.8)),
((-93.2,72.8),(-95.4,72.1),(-96.0,73.4),(-90.5,73.9),(-93.2,72.8)),
((-120.5,71.4),(-125.9,71.9),(-123.9,73.7),(-124.9,74.3),(-115.5,73.5),(-120.5,71.4)),
((-98.5,76.7),(-98.2,75),(-102.5,75.6),(-98.5,76.7)),
((-108.2,76.2),(-105.7,75.5),(-117.7,75.2),(-115.4,76.5),(-108.2,76.2)),
((57.5,70.7),(51.5,72.0),(55.6,75.1),(68.9,76.5),(58.5,74.3),(55.4,72.4),(57.5,70.7)),
((-94.7,77.1),(-79.8,74.9),(-89.8,74.5),(-97.1,76.8),(-94.7,77.1)),
((107.0,77.0),(114.1,75.8),(109.4,74.2),(127.0,73.6),(131.3,70.8),(139.9,71.5),(139.1,72.4),(140.5,72.8),(159.0,70.9),(160.9,69.4),(175.7,69.9),(180,69.0),(180,65.0),(177.4,64.6),(179.2,62.3),(170.3,59.9),(163.5,59.9),(162.0,58.2),(163.1,56.2),(156.8,51.0),(155.9,56.8),(164.5,62.6),(160.1,60.5),(159.3,61.8),(156.7,61.4),(154.2,59.8),(155.0,59.1),(142.2,59.0),(135.1,54.7),(139.9,54.2),(141.4,52.2),(136.9,45.1),(127.5,39.8),(129.1,35.1),(126.5,34.4),(125.3,39.6),(121.1,38.9),(121.6,40.9),(118.0,39.2),(118.9,37.4),(122.4,37.5),(119.2,34.9),(121.9,31.7),(121.7,28.2),(115.9,22.8),(110.4,20.3),(108.1,21.6),(105.9,19.8),(108.9,15.3),(109.2,11.7),(105.2,8.6),(100.1,13.4),(99.2,9.2),(103.4,4.9),(104.2,1.3),(101.4,2.8),(98.3,7.8),(97.2,16.9),(94.2,16.0),(91.4,22.8),(87.0,21.5),(80.3,15.9),(79.9,10.4),(77.5,8.0),(73.5,16.0),(72.6,21.4),(70.5,20.9),(66.4,25.4),(57.4,25.7),(57.0,27.0),(53.5,26.8),(50.1,30.1),(48.0,30.0),(51.8,24.0),(56.4,26.4),(56.8,24.2),(59.8,22.3),(55.3,17.2),(43.5,12.6),(42.3,17.5),(34.6,28.1),(35.0,29.4),(33.9,27.6),(32.4,29.9),(37.5,18.6),(42.7,11.7),(44.6,10.4),(51.1,12.0),(51.0,10.6),(48.6,5.3),(39.2,-4.7),(40.8,-14.7),(34.8,-19.8),(35.5,-24.1),(32.6,-25.7),(32.2,-28.8),(25.8,-33.9),(18.4,-34.1),(11.8,-18.1),(13.7,-10.7),(8.8,-1.1),(9.8,3.1),(4.3,6.3),(-9.0,4.8),(-16.7,12.4),(-17.0,21.9),(-5.9,35.8),(9.5,37.4),(11.1,36.9),(10.3,33.8),(19.1,30.3),(21.5,32.8),(33.8,31.0),(36.2,36.7),(29.7,36.1),(27.6,36.7),(26.2,39.5),(33.5,42.0),(38.3,40.9),(41.7,42.0),(36.7,45.2),(39.1,47.3),(35.0,46.3),(36.3,45.1),(33.9,44.4),(32.5,45.3),(33.6,45.9),(30.7,46.6),(27.7,42.6),(28.8,41.1),(22.6,40.3),(24.0,37.7),(22.5,36.4),(19.4,41.9),(13.1,45.7),(12.6,44.1),(18.5,40.2),(16.9,40.4),(16.1,38.0),(15.4,40.0),(8.9,44.4),(3.1,43.1),(-2.1,36.7),(-8.9,36.9),(-9.4,43.0),(-1.4,44.0),(-1.2,46.0),(-4.6,48.7),(-1.6,48.6),(-1.9,49.8),(8.1,53.5),(8.5,57.1),(10.6,57.7),(9.7,55.5),(10.9,54.0),(19.7,54.4),(21.6,57.4),(24.1,57.0),(23.3,59.2),(29.1,60.0),(21.3,60.7),(21.5,63.2),(25.4,65.1),(22.2,65.7),(17.8,62.7),(17.1,61.3),(18.8,60.1),(15.9,56.1),(12.9,55.4),(10.4,59.5),(5.7,58.6),(5.0,62.0),(16.4,68.6),(24.5,71.0),(41.1,67.5),(38.4,66.0),(33.2,66.6),(37.0,63.8),(37.2,65.1),(43.9,66.1),(43.5,68.6),(46.3,68.3),(46.3,66.7),(53.7,68.9),(59.9,68.3),(60.6,69.9),(68.5,68.1),(66.7,71.0),(72.6,72.8),(71.8,71.4),(73.7,68.4),(71.3,66.3),(72.4,66.2),(75.1,67.8),(73.1,71.4),(74.7,72.8),(75.3,71.3),(81.5,71.8),(80.5,73.6),(86.8,73.9),(87.2,75.1),(107.0,77.0)),
((105.1,78.3),(99.4,77.9),(102.1,79.3),(105.1,78.3)),
((18.3,79.7),(21.5,79.0),(15.9,76.8),(10.4,79.7),(18.3,79.7)),
((25.4,80.4),(27.4,80.1),(17.4,80.3),(25.4,80.4)),
((99.9,78.9),(91.2,80.3),(95.9,81.3),(99.9,78.9)),
((-87.0,79.7),(-85.8,79.3),(-92.9,78.3),(-96.7,80.2),(-92.4,81.3),(-87.0,79.7)),
((-68.5,83.1),(-61.9,82.4),(-76.9,79.3),(-75.4,78.5),(-80.6,76.2),(-89.5,76.5),(-88.3,77.9),(-85.0,77.5),(-88.0,78.4),(-85.1,79.3),(-86.9,80.3),(-81.8,80.5),(-91.6,81.9),(-68.5,83.1)),
((-27.1,83.5),(-20.8,82.7),(-31.9,82.2),(-12.2,81.3),(-20.0,80.2),(-17.7,80.1),(-19.7,78.8),(-18.5,77.0),(-21.7,76.6),(-19.4,74.3),(-24.8,72.3),(-21.8,70.7),(-25.5,71.4),(-26.4,70.2),(-22.3,70.1),(-39.8,65.5),(-43.4,60.1),(-48.3,60.9),(-51.6,63.6),(-54.0,67.2),(-50.9,69.9),(-54.7,69.6),(-54.4,70.8),(-51.4,70.6),(-55.8,71.7),(-54.7,72.6),(-58.6,75.5),(-68.5,76.1),(-71.4,77.0),(-66.8,77.4),(-73.3,78.0),(-65.7,79.4),(-68.0,80.1),(-62.7,81.8),(-27.1,83.5)),
]

# Region colours for list numbers 14-43 and their map pins.
RCOL = {
    "EUR": (178, 34, 34),
    "AME": (30, 90, 180),
    "ME": (220, 120, 20),
    "ASIA": (30, 140, 70),
    "AFR": (140, 80, 180),
    "OCE": (20, 140, 150),
    "WORLD": (110, 110, 110),
}

CARDS = [
    dict(place="ANTALYA, TURKIYE", tag="CLIMATE", tag2="COP31: OVERTIME",
         badge="DAY 13 OF 12",
         head="COP31 runs into overtime with no deal",
         body="The draft text lost its fossil-fuel language as talks ran past the deadline. (AP, Al Jazeera)",
         scene="cop"),
    dict(place="RIYADH", tag="MISSILES", tag2="RIYADH: 3 DOWNED",
         badge="3 INTERCEPTED",
         head="Coalition downs three missiles over Riyadh",
         body="Saudi-led defences intercepted three Houthi missiles aimed at the capital before dawn. (Reuters)",
         scene="riyadh"),
    dict(place="JUNIN, PERU", tag="QUAKE", tag2="PERU: M6.7",
         badge="M6.7",
         head="Magnitude 6.7 earthquake shakes central Peru",
         body="The deep quake struck at 00:09 GMT near Junin, felt in Lima. No deaths reported. (USGS)",
         scene="quake"),
    dict(place="KYIV", tag="", tag2="",
         badge="42 HURT",
         head="Russia hits Kyiv again as Kryvyi Rih counts its",
         body="Missiles set homes ablaze in Kyiv; 42 hurt in Kryvyi Rih. (Kyiv Post)",
         strip="REPORTED", scene="kyiv"),
    dict(place="DAVAO", tag="", tag2="",
         badge="146 SAFE",
         head="146 walk away after jet fire",
         body="Cebu Pacific jet shut an engine down and landed safely. (Philstar)",
         strip="OFFICIAL", scene="jet"),
    dict(place="MERCURY", tag="", tag2="",
         badge="FLYBY 6",
         head="BepiColombo beams back new Mercury photos",
         body="The probe's final flyby sets up orbit insertion in 2027. (ESA)",
         strip="OFFICIAL", scene="mercury"),
    dict(place="WARSAW", tag="", tag2="",
         badge="NATO ALERT",
         head="Poland calls NATO talks after drone falls",
         body="Debris fell in Poland; NATO calls it a grave violation. (Reuters)",
         strip="OFFICIAL", scene="poland"),
    dict(place="LAS VEGAS", tag="", tag2="",
         badge="RACE NIGHT",
         head="Vegas GP: Verstappen fastest, Norris on pole",
         body="Title rivals split practice in Las Vegas as the race tightens. (F1)",
         strip="OFFICIAL", scene="vegas"),
    dict(place="WELLINGTON", tag="", tag2="",
         badge="136 RUNS",
         head="Rahul's 136 puts India in charge of the first Test",
         body="Rahul's century gave India a first-innings lead. (ESPNcricinfo)",
         strip="OFFICIAL", scene="cricket"),
    dict(place="BAYELSA", tag="", tag2="",
         badge="BOAT LOST",
         head="Boat carrying mourners capsizes in Bayelsa",
         body="A boat of mourners capsized in Bayelsa. (Punch)",
         strip="REPORTED", scene="boat"),
    dict(place="BITCOIN", tag="", tag2="",
         badge="$58,983",
         head="Bitcoin slides below $59,000 in the AI rout",
         body="Bitcoin fell 3.9% in 24 hours as the Nasdaq sank 5.28%. (CoinDesk)",
         strip="REPORTED", scene="bitcoin"),
    dict(place="HORMUZ", tag="", tag2="",
         badge="US DENIES",
         head="US denies Iran downed a Reaper drone",
         body="Iran claimed it downed an MQ-9; US officials deny it. (Reuters)",
         strip="CLAIM", scene="hormuz"),
    dict(place="CANBERRA", tag="", tag2="",
         badge="AI TALKS",
         head="Australia and China hold rare talks on AI safety",
         body="Canberra and Beijing agreed to keep talking on AI risks. (Reuters)",
         strip="OFFICIAL", scene="aitalks"),
]

# (number, text, region, lon, lat) — list pins share the number's region colour.
# Left column shortened so no item reaches the right column.
MORE = [
    (14, "Zelensky warns Crimea bridge 'won't stay' (NBC)", "EUR", 29, 49),
    (15, "France arrests terror suspect in ex-spy plot (AFP)", "EUR", 2.4, 48.9),
    (16, "Measles: US loses elimination status (CDC)", "AME", -84.4, 33.8),
    (17, "Sydney police hunt car after Bondi shooting (ABC)", "OCE", 151.2, -33.9),
    (18, "Riyadh: Houthi warhead parts recovered (SPA)", "ME", 46.7, 24.7),
    (19, "UK judge okays Bayer's $7.25bn deal (Reuters)", "EUR", -0.1, 51.5),
    (20, "Zelensky-Rubio meet in Geneva (Reuters)", "EUR", 6.1, 46.2),
    (21, "Trump: $2,000 tariff dividend checks (NBC)", "AME", -77, 38.9),
    (22, "1 dead in Berlin train station stabbing (Bild)", "EUR", 13.4, 52.5),
    (23, "UK-EU sign biggest post-Brexit agreements (BBC)", "EUR", 4.4, 50.9),
    (24, "ICJ: Myanmar committed Rohingya genocide (ICJ)", "EUR", 4.3, 52.1),
    (25, "FBI: US police database exposed in hack (Reuters)", "AME", -87.6, 41.9),
    (26, "Australia: 5 die in house fire, murder charges (ABC)", "OCE", 145, -37.8),
    (27, "Drone hits Zaporizhzhia plant district (Kyiv Post)", "EUR", 35.2, 47.8),
    (28, "15 die in Hyderabad chemical plant fire (NDTV)", "ASIA", 78.5, 17.4),
    (29, "Markets: S&P 500 falls 3.7% in the AI rout (Reuters)", "AME", -76, 39),
    (30, "Nvidia: shares slide ~14% after record run (Bloomberg)", "AME", -121.9, 37.3),
    (31, "Gold: falls 4.62% to $3,515.4 an ounce (Bloomberg)", "WORLD", 8.5, 47.4),
    (32, "Anthropic: shares dip 8.5% after its $2tn IPO debut (CNBC)", "AME", -122.4, 37.8),
    (33, "COP31: small-island states demand a fossil phase-out (AP)", "WORLD", 28, 38),
    (34, "Poland: PM Tusk calls it a deliberate provocation (BBC)", "EUR", 19, 52),
    (35, "Turin: Sinner beats Alcaraz to reach the ATP final (AP)", "EUR", 7.7, 45.1),
    (36, "Argentina: country risk tops 1,000 (Reuters)", "AME", -58.4, -34.6),
    (37, "Haiti: Salvadoran troops hit by explosives, 3 hurt (AP)", "AME", -72.3, 18.5),
    (38, "Gen Z protests in 25 European countries (Euronews)", "EUR", 10, 50),
    (39, "CERN: first ultra-rare particle decay observed (CERN)", "EUR", 9, 47.5),
    (40, "US: Agriculture Dept hit in a cyberattack (Reuters)", "AME", -80, 37),
    (41, "Australia: police search for a missing hiker (ABC)", "OCE", 115.9, -32),
    (42, "Space: Blue Origin 6th crewed flight launches (Space.com)", "AME", -104, 31),
    (43, "Gaza: aid trucks enter as ceasefire holds (Reuters)", "ME", 34.5, 31.5),
]

# Card pins 1-13 (red, numbered) as (lon, lat).
PINS = {1: (32, 34), 2: (45, 20), 3: (-75.5, -11.2), 4: (32, 52), 5: (125.6, 7.1),
        6: (8.6, 49.9), 7: (21, 52.2), 8: (-115.1, 36.2), 9: (174.8, -41.3),
        10: (6.3, 4.9), 11: (-74, 40.7), 12: (60, 28), 13: (149.1, -35.3)}


def scene_cop(d, x, y, w, h):
    # COP31 summit hall at dusk: detailed globe, flags, warm spotlights.
    vgrad(d, (x, y, x + w, y + h), (24, 42, 92), (120, 70, 60))
    for bx in (0.0, 0.88):
        d.polygon([(x + w * bx, y + h), (x + w * (bx + 0.07), y + h * 0.3),
                   (x + w * (bx + 0.14), y + h)],
                  fill=(255, 230, 170))
    cx, cy, r = x + w * 0.5, y + h * 0.5, w * 0.18
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(40, 90, 170))
    d.ellipse([cx - r * 0.55, cy - r * 0.75, cx + r * 0.1, cy - r * 0.1],
              fill=(70, 160, 100))
    d.ellipse([cx + r * 0.1, cy + r * 0.05, cx + r * 0.7, cy + r * 0.55],
              fill=(90, 140, 80))
    d.ellipse([cx - r * 0.85, cy + r * 0.15, cx - r * 0.3, cy + r * 0.5],
              fill=(150, 130, 70))
    d.ellipse([cx - r * 0.7, cy - r * 0.8, cx - r * 0.35, cy - r * 0.5],
              fill=(255, 255, 255))
    d.ellipse([cx + r * 0.15, cy - r * 0.2, cx + r * 0.75, cy + r * 0.1],
              fill=(255, 255, 255))
    d.ellipse([cx - r * 0.3, cy - r * 0.35, cx + r * 0.25, cy + r * 0.15],
              fill=(255, 255, 255))
    d.rectangle([x, y + h * 0.82, x + w, y + h], fill=(40, 30, 25))
    for i, c in enumerate([(200, 40, 40), (30, 90, 180), (255, 255, 255),
                           (30, 140, 70), (255, 200, 40), (140, 80, 180),
                           (220, 120, 20), (200, 40, 40)]):
        fx = x + w * (0.06 + i * 0.115)
        d.line([fx, y + h * 0.82, fx, y + h * 0.66], fill=(200, 190, 170),
               width=2 * SS)
        d.rectangle([fx, y + h * 0.66, fx + w * 0.07, y + h * 0.8], fill=c)


def scene_riyadh(d, x, y, w, h):
    # Riyadh at night: stars, tower skyline, missile trails, interception bursts.
    vgrad(d, (x, y, x + w, y + h), (8, 12, 40), (60, 30, 70))
    for sx, sy in [(0.08, 0.1), (0.22, 0.2), (0.35, 0.08), (0.6, 0.15),
                   (0.75, 0.07), (0.9, 0.18), (0.45, 0.25), (0.95, 0.3)]:
        d.ellipse([x + w * sx, y + h * sy, x + w * (sx + 0.012),
                   y + h * (sy + 0.016)], fill=(255, 255, 255))
    # Kingdom Centre tower with its arch opening
    tx = x + w * 0.42
    d.rectangle([tx, y + h * 0.12, tx + w * 0.16, y + h * 0.98],
                fill=(25, 25, 45))
    d.polygon([(tx + w * 0.02, y + h * 0.12), (tx + w * 0.08, y + h * 0.28),
               (tx + w * 0.14, y + h * 0.12)], fill=(8, 12, 40))
    for wy in range(0, 12):
        d.rectangle([tx + w * 0.03, y + h * (0.32 + wy * 0.05),
                     tx + w * 0.05, y + h * (0.35 + wy * 0.05)],
                    fill=(255, 200, 80))
        d.rectangle([tx + w * 0.11, y + h * (0.32 + wy * 0.05),
                     tx + w * 0.13, y + h * (0.35 + wy * 0.05)],
                    fill=(255, 200, 80))
    for bx, bw, bh in [(0.02, 0.14, 0.45), (0.2, 0.1, 0.35), (0.62, 0.12, 0.5),
                       (0.78, 0.18, 0.38)]:
        d.rectangle([x + w * bx, y + h * (0.98 - bh), x + w * (bx + bw), y + h],
                    fill=(20, 20, 38))
        for k in range(4):
            d.rectangle([x + w * (bx + 0.02 + k * 0.03),
                         y + h * (0.98 - bh + 0.05),
                         x + w * (bx + 0.035 + k * 0.03),
                         y + h * (0.98 - bh + 0.09)], fill=(255, 200, 80))
    # missile trails with smoke
    for (x1, y1, x2, y2) in [(0.08, 0.3, 0.3, 0.55), (0.55, 0.18, 0.72, 0.42),
                             (0.8, 0.3, 0.92, 0.5)]:
        d.line([x + w * x1, y + h * y1, x + w * x2, y + h * y2],
               fill=(255, 230, 150), width=3 * SS)
        d.ellipse([x + w * (x2 - 0.02), y + h * (y2 - 0.02),
                   x + w * (x2 + 0.05), y + h * (y2 + 0.05)],
                  fill=(255, 160, 60))
    # interception bursts
    for bx, by in [(0.3, 0.55), (0.72, 0.42)]:
        d.ellipse([x + w * (bx - 0.05), y + h * (by - 0.06),
                   x + w * (bx + 0.05), y + h * (by + 0.06)],
                  fill=(255, 200, 90))
        for a in range(8):
            ang = a * math.pi / 4
            d.line([x + w * bx, y + h * by,
                    x + w * bx + math.cos(ang) * w * 0.07,
                    y + h * by + math.sin(ang) * h * 0.09],
                   fill=(255, 220, 120), width=2 * SS)


def scene_quake(d, x, y, w, h):
    # Andes at dawn: layered ridges, cracked ground, seismograph, dust.
    vgrad(d, (x, y, x + w, y + h), (220, 180, 130), (90, 60, 40))
    d.polygon([(x, y + h * 0.55), (x + w * 0.15, y + h * 0.2),
               (x + w * 0.3, y + h * 0.5), (x + w * 0.5, y + h * 0.15),
               (x + w * 0.7, y + h * 0.45), (x + w * 0.85, y + h * 0.25),
               (x + w, y + h * 0.55), (x + w, y + h), (x, y + h)],
              fill=(120, 90, 60))
    d.polygon([(x, y + h * 0.7), (x + w * 0.2, y + h * 0.4),
               (x + w * 0.45, y + h * 0.65), (x + w * 0.65, y + h * 0.38),
               (x + w * 0.85, y + h * 0.62), (x + w, y + h * 0.7),
               (x + w, y + h), (x, y + h)], fill=(80, 55, 35))
    d.polygon([(x + w * 0.12, y + h * 0.16), (x + w * 0.15, y + h * 0.2),
               (x + w * 0.18, y + h * 0.16)], fill=(255, 255, 255))
    d.polygon([(x + w * 0.47, y + h * 0.11), (x + w * 0.5, y + h * 0.15),
               (x + w * 0.53, y + h * 0.11)], fill=(255, 255, 255))
    # cracked foreground road
    d.polygon([(x, y + h * 0.78), (x + w, y + h * 0.72), (x + w, y + h),
               (x, y + h)], fill=(45, 30, 20))
    d.line([(x + w * 0.1, y + h * 0.78), (x + w * 0.25, y + h * 0.85),
            (x + w * 0.2, y + h * 0.95), (x + w * 0.35, y + h)],
           fill=(220, 200, 170), width=2 * SS)
    d.line([(x + w * 0.6, y + h * 0.75), (x + w * 0.7, y + h * 0.85),
            (x + w * 0.65, y + h * 0.95)], fill=(220, 200, 170), width=2 * SS)
    # seismograph trace
    pts = []
    for i in range(11):
        px = x + w * (0.05 + i * 0.09)
        py = y + h * (0.45 + 0.12 * ((i % 2) * 2 - 1) * (1 if i % 3 else 0.3))
        pts.append((px, py))
    d.line(pts, fill=(255, 60, 60), width=4 * SS, joint="curve")
    # dust clouds + a tilted house
    for dx, dy, r in [(0.25, 0.62, 0.05), (0.7, 0.58, 0.06), (0.85, 0.68, 0.04)]:
        d.ellipse([x + w * (dx - r), y + h * (dy - r * 0.6),
                   x + w * (dx + r), y + h * (dy + r * 0.6)],
                  fill=(200, 170, 120))
    d.polygon([(x + w * 0.44, y + h * 0.66), (x + w * 0.52, y + h * 0.66),
               (x + w * 0.52, y + h * 0.76), (x + w * 0.44, y + h * 0.76)],
              fill=(180, 140, 90))
    d.polygon([(x + w * 0.42, y + h * 0.66), (x + w * 0.48, y + h * 0.6),
               (x + w * 0.54, y + h * 0.66)], fill=(120, 50, 40))


def scene_kyiv(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (30, 30, 50), (120, 50, 30))
    for cx, cy, s in [(0.15, 0.25, 0.09), (0.5, 0.15, 0.11), (0.82, 0.3, 0.08)]:
        d.ellipse([x + w * cx, y + h * cy, x + w * (cx + s), y + h * (cy + s)],
                  fill=(255, 160, 40))
    d.rectangle([x + w * 0.08, y + h * 0.62, x + w * 0.2, y + h * 0.98],
                fill=(30, 30, 40))
    d.rectangle([x + w * 0.42, y + h * 0.55, x + w * 0.55, y + h * 0.98],
                fill=(30, 30, 40))
    d.rectangle([x + w * 0.75, y + h * 0.66, x + w * 0.9, y + h * 0.98],
                fill=(30, 30, 40))
    d.rectangle([x, y + h * 0.94, x + w, y + h], fill=(20, 20, 25))


def scene_jet(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (120, 180, 230), (200, 220, 245))
    d.polygon([(x + w * 0.1, y + h * 0.55), (x + w * 0.75, y + h * 0.4),
               (x + w * 0.95, y + h * 0.45), (x + w * 0.75, y + h * 0.6),
               (x + w * 0.1, y + h * 0.75)], fill=(240, 245, 250))
    d.polygon([(x + w * 0.3, y + h * 0.4), (x + w * 0.5, y + h * 0.25),
               (x + w * 0.55, y + h * 0.45)], fill=(200, 210, 220))
    d.ellipse([x + w * 0.85, y + h * 0.35, x + w * 0.95, y + h * 0.55],
              fill=(255, 140, 40))
    d.rectangle([x, y + h * 0.8, x + w, y + h], fill=(80, 120, 60))


def scene_mercury(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (10, 10, 25), (40, 30, 50))
    d.ellipse([x + w * 0.3, y + h * 0.2, x + w * 0.7, y + h * 0.8],
              fill=(150, 110, 80))
    for cx, cy, r in [(0.4, 0.35, 0.04), (0.55, 0.5, 0.05), (0.45, 0.65, 0.03),
                      (0.6, 0.32, 0.03)]:
        d.ellipse([x + w * (cx - r), y + h * (cy - r), x + w * (cx + r),
                   y + h * (cy + r)], fill=(110, 80, 55))
    d.line([x + w * 0.1, y + h * 0.8, x + w * 0.9, y + h * 0.9],
           fill=(255, 255, 255), width=2 * SS)


def scene_poland(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (40, 80, 50), (120, 160, 110))
    d.rectangle([x + w * 0.08, y + h * 0.15, x + w * 0.42, y + h * 0.55],
                fill=(255, 255, 255))
    d.rectangle([x + w * 0.08, y + h * 0.35, x + w * 0.42, y + h * 0.55],
                fill=RED)
    d.rectangle([x + w * 0.55, y + h * 0.15, x + w * 0.9, y + h * 0.35],
                fill=(30, 60, 160))
    d.rectangle([x + w * 0.55, y + h * 0.35, x + w * 0.9, y + h * 0.55],
                fill=RED)
    d.rectangle([x, y + h * 0.8, x + w, y + h], fill=(60, 90, 50))


def scene_vegas(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (40, 20, 80), (120, 30, 90))
    d.rectangle([x + w * 0.05, y + h * 0.15, x + w * 0.95, y + h * 0.55],
                fill=(200, 30, 30))
    d.rectangle([x + w * 0.1, y + h * 0.2, x + w * 0.3, y + h * 0.5],
                fill=(255, 220, 0))
    d.rectangle([x + w * 0.65, y + h * 0.55, x + w * 0.8, y + h * 0.65],
                fill=(20, 20, 20))
    d.rectangle([x + w * 0.75, y + h * 0.58, x + w * 0.88, y + h * 0.68],
                fill=(20, 20, 20))
    d.rectangle([x, y + h * 0.72, x + w, y + h], fill=(30, 20, 40))


def scene_cricket(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (120, 200, 120), (40, 100, 50))
    d.rectangle([x + w * 0.3, y + h * 0.2, x + w * 0.34, y + h * 0.8],
                fill=(200, 160, 100))
    d.rectangle([x + w * 0.32, y + h * 0.28, x + w * 0.62, y + h * 0.38],
                fill=(200, 160, 100))
    d.ellipse([x + w * 0.68, y + h * 0.5, x + w * 0.74, y + h * 0.58],
              fill=(180, 40, 40))
    d.rectangle([x, y + h * 0.82, x + w, y + h], fill=(30, 80, 40))


def scene_boat(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (140, 200, 240), (60, 110, 160))
    for yy in (0.3, 0.45, 0.6):
        d.line([(x, y + h * yy), (x + w, y + h * (yy + 0.06))],
               fill=(255, 255, 255), width=2 * SS)
    d.polygon([(x + w * 0.2, y + h * 0.55), (x + w * 0.8, y + h * 0.55),
               (x + w * 0.7, y + h * 0.75), (x + w * 0.3, y + h * 0.75)],
              fill=(120, 70, 30))
    d.line([x + w * 0.5, y + h * 0.55, x + w * 0.5, y + h * 0.3],
           fill=(80, 50, 20), width=3 * SS)


def scene_bitcoin(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (30, 40, 70), (90, 60, 100))
    d.ellipse([x + w * 0.35, y + h * 0.15, x + w * 0.65, y + h * 0.75],
              fill=(255, 170, 30))
    d.text((x + w * 0.46, y + h * 0.22), "B", font=SANS_B(22), fill=(120, 70, 0))
    pts = [(x + w * 0.05, y + h * 0.75), (x + w * 0.25, y + h * 0.5),
           (x + w * 0.45, y + h * 0.65), (x + w * 0.7, y + h * 0.35),
           (x + w * 0.95, y + h * 0.55)]
    d.line(pts, fill=RED, width=4 * SS, joint="curve")


def scene_hormuz(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (80, 140, 190), (20, 60, 100))
    d.polygon([(x + w * 0.2, y + h * 0.6), (x + w * 0.5, y + h * 0.25),
               (x + w * 0.8, y + h * 0.6)], fill=(220, 220, 220))
    d.ellipse([x + w * 0.42, y + h * 0.42, x + w * 0.58, y + h * 0.6],
              fill=(60, 60, 60))
    d.rectangle([x, y + h * 0.8, x + w, y + h], fill=(20, 50, 80))


def scene_aitalks(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (20, 30, 70), (70, 50, 110))
    d.ellipse([x + w * 0.15, y + h * 0.2, x + w * 0.45, y + h * 0.7],
              fill=(120, 80, 200))
    d.ellipse([x + w * 0.55, y + h * 0.2, x + w * 0.85, y + h * 0.7],
              fill=(40, 150, 80))
    d.text((x + w * 0.24, y + h * 0.32), "AI", font=SANS_B(18),
           fill=(255, 255, 255))
    d.text((x + w * 0.64, y + h * 0.32), "AU", font=SANS_B(18),
           fill=(255, 255, 255))


SCENES = {"cop": scene_cop, "riyadh": scene_riyadh, "quake": scene_quake,
          "kyiv": scene_kyiv, "jet": scene_jet, "mercury": scene_mercury,
          "poland": scene_poland, "vegas": scene_vegas,
          "cricket": scene_cricket, "boat": scene_boat,
          "bitcoin": scene_bitcoin, "hormuz": scene_hormuz,
          "aitalks": scene_aitalks}


def card_frame(d, x, y, w, frame_h, pic_h, card, num, hero):
    d.rectangle([x, y, x + w, y + frame_h], fill=PAPER, outline=(200, 192, 172),
                width=2 * SS)
    SCENES[card["scene"]](d, x, y, w, pic_h)
    # badge, top-right inside the picture
    bw = d.textlength(card["badge"], font=SANS_B(9)) + 12 * SS
    d.rectangle([x + w - bw, y, x + w, y + 15 * SS], fill=RED)
    d.text((x + w - bw + 6 * SS, y + 2 * SS), card["badge"], font=SANS_B(9),
           fill=(255, 255, 255))
    tx = x + 10 * SS
    ty = y + pic_h + 8 * SS
    if hero:
        tag = f"{num}  {card['place']} · {card['tag']} — {card['tag2']}"
        d.text((tx, ty), tag, font=SANS_B(10), fill=RED)
        ty += 20 * SS
        hf, bf = SERIF_B(15), SANS(11)
    else:
        d.text((tx, ty), f"{num}  {card['place']}", font=SANS_B(10), fill=RED)
        ty += 20 * SS
        hf, bf = SERIF_B(12), SANS(9)
    heads = wrap(d, card["head"], hf, w - 20 * SS)
    hpitch = 18 * SS if hero else 15 * SS
    for ln in heads:
        d.text((tx, ty), ln, font=hf, fill=INK)
        ty += hpitch
    bodies = wrap(d, card["body"], bf, w - 20 * SS)
    bpitch = 14 * SS if hero else 13 * SS
    for ln in bodies:
        d.text((tx, ty), ln, font=bf, fill=(50, 48, 44))
        ty += bpitch
    if not hero:
        # tag strip at the bottom of medium cards
        col = {"REPORTED": RED, "OFFICIAL": (30, 90, 180),
               "CLAIM": RED}[card["strip"]]
        sw = d.textlength(card["strip"], font=SANS_B(8)) + 8 * SS
        d.rectangle([tx, y + frame_h - 16 * SS, tx + sw, y + frame_h - 2 * SS],
                    outline=col, width=2 * SS)
        d.text((tx + 4 * SS, y + frame_h - 14 * SS), card["strip"],
               font=SANS_B(8), fill=col)
    return (len(heads), len(bodies))


def draw_map(d, x, y, w, h):
    # fresh blue sea, real continents
    d.rectangle([x, y, x + w, y + h], fill=SEA)
    for poly in CONTINENTS:
        d.polygon([(x + (lon + 180) / 360 * w, y + (90 - lat) / 180 * h)
                   for lon, lat in poly], fill=LANDC)
    for n, (lon, lat) in PINS.items():
        cx = x + (lon + 180) / 360 * w
        cy = y + (90 - lat) / 180 * h
        d.ellipse([cx - 7 * SS, cy - 7 * SS, cx + 7 * SS, cy + 7 * SS], fill=RED,
                  outline=(255, 255, 255), width=2 * SS)
        d.text((cx - 4 * SS, cy - 6 * SS), str(n), font=SANS_B(7),
               fill=(255, 255, 255))
    for n, t, reg, lon, lat in MORE:
        cx = x + (lon + 180) / 360 * w
        cy = y + (90 - lat) / 180 * h
        d.ellipse([cx - 3 * SS, cy - 3 * SS, cx + 3 * SS, cy + 3 * SS],
                  fill=RCOL[reg], outline=(255, 255, 255), width=1 * SS)


def build():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    # red header band
    d.rectangle([0, 0, W, 140 * SS], fill=RED)
    d.text((MX, 24), "THE WORLD TODAY", font=SANS_B(30), fill=(255, 255, 255))
    d.text((MX, 110),
           "SATURDAY 21 NOVEMBER 2026  •  43 STORIES  •  7 REGIONS  •  13 ILLUSTRATED CARDS",
           font=SANS_B(15), fill=(255, 255, 255))
    d.text((MX, 170),
           "One image. Every story checked against the sources named under each card.",
           font=SANS(11), fill=(255, 255, 255))
    d.text((MX, 200),
           "Red numbers mark stories 1-13. Full list 14-43 below.  •  make.fun",
           font=SANS(11), fill=(255, 255, 255))
    d.text((MX, 250),
           "SOURCES: AP, REUTERS, BBC, AFP, USGS, ESA, F1, ESPNCRICINFO, COINDESK, KYIV POST",
           font=SANS(9), fill=(255, 220, 220))
    d.text((W - MX - d.textlength("NEWS IMAGE", font=SANS_B(9)), 250), "NEWS IMAGE",
           font=SANS_B(9), fill=(255, 255, 255))
    # heroes
    gap = 20
    hw = (W - 2 * MX - 2 * gap) // 3
    pic_h = 120 * SS
    frame_h = 210 * SS
    counts = []
    for i in range(3):
        counts.append(card_frame(d, MX + i * (hw + gap), 300, hw, frame_h, pic_h,
                                 CARDS[i], i + 1, True))
    # mediums
    mw = (W - 2 * MX - 4 * gap) // 5
    mpic = 90 * SS
    mframe = 190 * SS
    for row in range(2):
        for col in range(5):
            idx = 3 + row * 5 + col
            counts.append(card_frame(d, MX + col * (mw + gap), 740 + row * 400,
                                     mw, mframe, mpic, CARDS[idx], idx + 1, False))
    # bottom header
    d.text((MX, 1548), "WHERE IT HAPPENED", font=SANS_B(11), fill=INK)
    d.text((592, 1548), "ALSO ON SATURDAY", font=SANS_B(11), fill=INK)
    # map (real continents)
    draw_map(d, MX, 1584, 540, 270)
    d.text((MX, 1860), "PACIFIC", font=SANS(9), fill=MUT)
    d.text((MX + 540 - d.textlength("ATLANTIC", font=SANS(9)), 1860), "ATLANTIC",
           font=SANS(9), fill=MUT)
    # list — numbers coloured by region, synced with the map pins
    lx, colw = 592, 720
    for i, (n, t, reg, lon, lat) in enumerate(MORE):
        col = i // 15
        row = i % 15
        tx = lx + col * colw
        ty = 1578 + row * 22
        d.text((tx, ty), str(n), font=SANS_B(11), fill=RCOL[reg])
        d.text((tx + 26 * SS, ty), t, font=SANS(11), fill=(50, 48, 44))
    # date check box (with your count inside) + footer
    d.rectangle([MX, 1916, 1090, 2020], outline=RED, width=2 * SS)
    d.text((MX + 10 * SS, 1924), "DATE CHECK: all 43 stories, 21 Nov 2026.",
           font=SANS(11), fill=INK)
    d.text((MX + 10 * SS, 1948), "Friday news excluded. Sources on cards.",
           font=SANS(11), fill=INK)
    d.text((MX + 10 * SS, 1972), "13 cards above + 30 below = 43 stories.",
           font=SANS(11), fill=INK)
    d.text((MX + 10 * SS, 1996), "YOUR COUNT: 43 stories, 7 regions.",
           font=SANS_B(11), fill=INK)
    d.text((MX, 2028), "make.fun  •  The World Today  •  Saturday 21 November 2026",
           font=SANS(9), fill=GREY)
    out = img.resize((1024, 1024), Image.LANCZOS)
    grain(out, amp=4)
    out.save("entry.png", format="PNG")
    print("wrap counts (head, body) per card:", counts)
    print("saved entry.png")


if __name__ == "__main__":
    build()
