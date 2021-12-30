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
import json
from datetime import datetime


QUOTE_PATH = "/home/pi/workspace/stoic-epaper/parser/the-daily-stoic-clean.json"


quotes = [
        { "quote": "Every new beginning comes from some other benning's end.", "author" : "Seneca" },
        { "quote": "If it is not right, do not do it, if it is not true, do not say it.", "author" : "Marcus Aurelius" },
        { "quote": "When it comes to your goals and the things you strive for, ask yourself: Am I in control of them or they in control of me?", "author" : "Epictetus, Discourses, 4.4.1-2.15" }]

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

def getQuotes():
    quotes=[]
    with open(QUOTE_PATH) as json_file:
        quotes = json.load(json_file)
        # for quote in quotes:
            # print('date: ' + quote['date'])
            # print('title: ' + quote['title'])
            # print('quote: ' + quote['quote'])
            # print('commentary: ' + quote['commentary'])
            # print('')
    return quotes

def isLeapYear(year):
    if(year % 4) == 0:
        if(year % 100) == 0:
                if(year % 400) == 0:
                    return True
                else:
                    return False
        else:
            return True
    else:
        return False
        
def getDailyStoicQuote():
    quotes = getQuotes()

    # If it is not a leap year
    year = datetime.now().year
    if(isLeapYear(year) == False):
        # Yank Leap year day from quotes
        LEAP_YEAR_DAY = 60
        del quotes[LEAP_YEAR_DAY]
    
    dayOfYear = datetime.now().timetuple().tm_yday - 1
    quote = quotes[dayOfYear]
    # print('date: ' + quote['date'])
    # print('title: ' + quote['title'])
    # print('quote: ' + quote['quote'])
    # print('commentary: ' + quote['commentary'])
    # print('')
    return quote


def getStrings(printWidth, font, text):
    strings = []
    asciiText = text.encode("utf8","ignore")
    text = asciiText.decode()
    width = font.getsize(text)[0]
    numLines = (width + (printWidth-1)) // printWidth 
    # logging.debug("width %d", width)
    # logging.debug("numLines %d", numLines)
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


        
def updateScreen(quote):
    # Main Below
    try:
        # Get Driver for Screen
        logging.info("Daily Stoic Begin Updating Screen")
        epd = epd7in5_V2.EPD()
        
        # Clear what's currently on the Screen
        logging.info("Init and Clear screen")
        epd.init()
        # epd.Clear()

        # Set up drawing canvas
        Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
        draw = ImageDraw.Draw(Himage)

        
        # Build canvas with text
        canvisDone = False
        quoteStrings = []
        authorStrings = []
        quoteFontSize = 36
        authorFontSize = 34
        while (canvisDone == False):
            quoteFont = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), quoteFontSize) 
            authorFont = ImageFont.truetype(os.path.join(fontdir, 'Piboto-Italic.ttf'), authorFontSize)
            quoteStrings = getStrings(QUOTE_WIDTH,quoteFont, quote["quote"])
            authorStrings = getStrings(AUTHOR_WIDTH,authorFont," - " + quote["author"])
            offsetY = (MAX_LINES - len(quoteStrings) - len(authorStrings)) / 2 
            if((len(quoteStrings)+len(authorStrings)) > MAX_LINES):
                quoteFontSize = quoteFontSize - 2
                authorFontSize = authorFontSize - 2
            else:
                canvisDone = True

        s = 0
        while (s < len(quoteStrings)):
            draw.text((QUOTE_MARGIN_X, (offsetY + s)*LINE_HEIGHT), quoteStrings[s], font=quoteFont, fill=0)
            s = s+1

        a = 0
        while (a < len(authorStrings)):
            marginX = SCREEN_WIDTH - AUTHOR_MARGIN_X - authorFont.getsize(authorStrings[a])[0]
            draw.text((marginX, AUTHOR_OFFSET+((offsetY+s+a)*LINE_HEIGHT)), authorStrings[a], font = authorFont, fill = 0)
            a = a+1

        # Draw canvas on screen
        logging.info("Draw Daily Stoic Quote")
        epd.display(epd.getbuffer(Himage))
        time.sleep(3)

        # Put Screen to sleep
        logging.info("Goto Sleep...")
        epd.sleep()
        
    except IOError as e:
        logging.info(e)
        
    except KeyboardInterrupt:    
        logging.info("ctrl + c:")
        epd7in5_V2.epdconfig.module_exit()
        exit()

def testQuoteAuthorLength(quote):
    font36 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 36) 
    authorFont34 = ImageFont.truetype(os.path.join(fontdir, 'Piboto-Italic.ttf'), 34)
    quoteStrings = getStrings(QUOTE_WIDTH,font36, quote["quote"])
    authorStrings = getStrings(AUTHOR_WIDTH,authorFont34," - " + quote["author"])

    if((len(quoteStrings) + len(authorStrings)) > 12):
        font32 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 30) 
        authorFont28 = ImageFont.truetype(os.path.join(fontdir, 'Piboto-Italic.ttf'), 28)
        quoteStrings = getStrings(QUOTE_WIDTH,font32, quote["quote"])
        authorStrings = getStrings(AUTHOR_WIDTH,authorFont28," - " + quote["author"])

    if((len(quoteStrings) + len(authorStrings)) > 12):
        logging.debug(f"Date: {quote['date']}")
        logging.debug(f"Quote+Author Height = {len(quoteStrings) + len(authorStrings)}")
        return -1
    return 0

def testAuthorLongerThanQuote(quote):
    if(len(quote["author"]) > len(quote["quote"])):
        logging.debug(f"Date: {quote['date']}")
        logging.debug(f"Author: {quote['author']}")
        logging.debug(f"Quote: {quote['quote']}")
        return -1
    return 0

def testSplitFirstWord(quote):
    splitWords = quote["quote"].split(" ")
    if(len(splitWords[0]) == 1):
        logging.debug(f"Date: {quote['date']}")
        logging.debug(f"Quote: {splitWords[0]} {splitWords[1]}")
        return -2
    return 0


# Tests
def runTests():
    quotes = getQuotes()
    
    # Test Long Quotes
    #longQuotes = []
    #quoteIndex = 0
    #for quote in quotes:
    #    # logging.debug(f"Date: {quote['date']}")
    #    returnValue = testQuoteAuthorLength(quote)
    #    if (returnValue != 0):
    #        longQuotes.append(quote)
    #    quoteIndex = quoteIndex + 1

    #logging.debug("Long Quotes")
    #for quote in longQuotes:
    #    print(quote["date"])
     
        
    # Test Author longer than Quote
    #longAuthors = []
    #for quote in quotes:
    #    returnValue = testAuthorLongerThanQuote(quote)
    #    if (returnValue != 0):
    #        longAuthors.append(quote)

    #logging.debug("Long Authors")
    #for quote in longAuthors:
    #    print(quote["date"])
        
    # Test first word is split
    #singleCharacterFirstWord = []
    #for quote in quotes:
    #    returnValue = testSplitFirstWord(quote)
    #    if (returnValue != 0):
    #        singleCharacterFirstWord.append(quote)
    
    #logging.debug("Long Single Character First Words")
    #for quote in singleCharacterFirstWord:
    #    print(quote["date"])

def runTheDailyStoic():
    quote = getDailyStoicQuote()
    updateScreen(quote)

#runTests()
runTheDailyStoic()
