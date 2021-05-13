#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
fontdir = os.path.join("/usr/share/fonts/truetype/piboto/")
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd7in5_V2
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

quotes = [
        { "quote": "Every new beginning comes from some other benning's end.", "author" : "Seneca" },
        { "quote": "If it is not right, do not do it, if it is not true, do not say it.", "author" : "Marcus Aurelius" }]

logging.basicConfig(level=logging.DEBUG)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
QUOTE_MARGIN_X = 50
QUOTE_WIDTH = SCREEN_WIDTH - (2 * QUOTE_MARGIN_X)
AUTHOR_MARGIN_X = 120
AUTHOR_WIDTH = SCREEN_WIDTH - (2 * AUTHOR_MARGIN_X)
LINE_HEIGHT = 32
MAX_LINES = SCREEN_HEIGHT / LINE_HEIGHT
AUTHOR_OFFSET = 5

def getQuote():
    dayOfYear = datetime.now().timetuple().tm_yday


def getStrings(printWidth, font, text):
    strings = []
    width = font.getsize(text)[0]
    numLines = (width + (printWidth-1)) // printWidth
    logging.info("width %d", width)
    logging.info("numLines %d", numLines)
    i = 0
    wordCounter = 0
    while (i < numLines):
        newString = ""
        splitString = text.split(" ")
        while ((font.getsize(newString)[0] < printWidth) and
                (wordCounter < len(splitString))):
            if not newString:
                newString = splitString[wordCounter]
            else:
                newString = newString + " " + splitString[wordCounter]
            wordCounter = wordCounter + 1
        if(font.getsize(newString)[0] > printWidth):
            newString = newString.rsplit(' ', 1)[0]
            wordCounter = wordCounter - 1
        strings.append(newString)
        i = i + 1
    return strings


try:
    logging.info("epd7in5_V2 Demo")
    epd = epd7in5_V2.EPD()

    logging.info("init and Clear")
    epd.init()
    epd.Clear()

    font36 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 36)
    font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
    authorFont34 = ImageFont.truetype(os.path.join(fontdir, 'Piboto-Italic.ttf'), 34)
    # Drawing on the Horizontal image
    logging.info("1.Drawing on the Horizontal image...")
    Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(Himage)
    quoteStrings = getStrings(QUOTE_WIDTH,font36, quotes[0]["quote"])
    authorStrings = getStrings(AUTHOR_WIDTH,authorFont34," - " + quotes[0]["author"])
    offsetY = (MAX_LINES - len(quoteStrings) - len(authorStrings)) / 2
    s = 0
    while (s < len(quoteStrings)):
        draw.text((QUOTE_MARGIN_X, (offsetY + s)*LINE_HEIGHT), quoteStrings[s], font=font36, fill=0)
        s = s+1
    a = 0
    while (a < len(authorStrings)):
        marginX = SCREEN_WIDTH - AUTHOR_MARGIN_X - authorFont34.getsize(authorStrings[a])[0]
        draw.text((marginX, AUTHOR_OFFSET+((offsetY+s+a)*LINE_HEIGHT)), authorStrings[a], font = authorFont34, fill = 0)
        a = a+1
    # draw.text((150, 0), u'微雪电子', font = font24, fill = 0)
    # draw.line((20, 50, 70, 100), fill = 0)
    # draw.line((70, 50, 20, 100), fill = 0)
    # draw.rectangle((20, 50, 70, 100), outline = 0)
    # draw.line((165, 50, 165, 100), fill = 0)
    # draw.line((140, 75, 190, 75), fill = 0)
    # draw.arc((140, 50, 190, 100), 0, 360, fill = 0)
    # draw.rectangle((80, 50, 130, 100), fill = 0)
    # draw.chord((200, 50, 250, 100), 0, 360, fill = 0)
    epd.display(epd.getbuffer(Himage))
    time.sleep(10)

    # Drawing on the Vertical image
    # logging.info("2.Drawing on the Vertical image...")
    # Limage = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
    # draw = ImageDraw.Draw(Limage)
    # draw.text((2, 0), 'hello world', font = font18, fill = 0)
    # draw.text((2, 20), '7.5inch epd', font = font18, fill = 0)
    # draw.text((20, 50), u'微雪电子', font = font18, fill = 0)
    # draw.line((10, 90, 60, 140), fill = 0)
    # draw.line((60, 90, 10, 140), fill = 0)
    # draw.rectangle((10, 90, 60, 140), outline = 0)
    # draw.line((95, 90, 95, 140), fill = 0)
    # draw.line((70, 115, 120, 115), fill = 0)
    # draw.arc((70, 90, 120, 140), 0, 360, fill = 0)
    # draw.rectangle((10, 150, 60, 200), fill = 0)
    # draw.chord((70, 150, 120, 200), 0, 360, fill = 0)
    # epd.display(epd.getbuffer(Limage))
    # time.sleep(10)

    # logging.info("3.read bmp file")
    # Himage = Image.open(os.path.join(picdir, '7in5_V2.bmp'))
    # epd.display(epd.getbuffer(Himage))
    # time.sleep(2)

    # logging.info("4.read bmp file on window")
    # Himage2 = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
    # bmp = Image.open(os.path.join(picdir, '100x100.bmp'))
    # Himage2.paste(bmp, (50,10))
    # epd.display(epd.getbuffer(Himage2))
    # time.sleep(2)

    # logging.info("Clear...")
    # epd.init()
    # clear()

    logging.info("Goto Sleep...")
    epd.sleep()

except IOError as e:
    logging.info(e)

except KeyboardInterrupt:
    logging.info("ctrl + c:")
    epd7in5_V2.epdconfig.module_exit()
    exit()
