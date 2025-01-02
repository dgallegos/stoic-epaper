 #!/usr/bin/env python3

import sys
import os

# Add path
sys.path.append('../models')

# Import Models
from models.quote import Quote

DAILY_STOIC_CLEAN_PATH = "the-daily-stoic-clean.json"
START_DAY = 0

def cycleQuotes(jsonQuotes,startNumber):
    quoteNumber = startNumber
    cliInput = ""
    quote = jsonQuotes[quoteNumber]
    quote.display()
    while (input != "x"):
        cliInput = input("'n' for next or 'x' for exit... ").lower()
        if (cliInput == "n"):
            quoteNumber += 1
            print("=============\n\n\n")
            quote = jsonQuotes[quoteNumber]
            quote.display()

def authorTooLongTest(jsonQuotes,startNumber):
    quoteNumber = startNumber
    cliInput = ""
    while (input != "x"):
        quote = jsonQuotes[quoteNumber]
        if (len(quote.author) > len(quote.quote)):
            quote.display()

            cliInput = input("'n' for next or 'x' for exit... ").lower()
            if (cliInput == "n"):
                quoteNumber += 1
                print("\n\n=============\n\n")
                # quote = jsonQuotes[quoteNumber]
                # quote.display()
        else:
            quoteNumber += 1
        
        # Check if done
        if quoteNumber >= len(jsonQuotes):
            print("got em!")
            return



# main
def main():
    print("hello")
    # read file into memory/JSON
    jsonQuotes = Quote.GetQuotesFromFile(os.path.join(os.path.dirname(os.path.abspath(__file__)),DAILY_STOIC_CLEAN_PATH))
    
    # Dispaly the quotes
    cycleQuotes(jsonQuotes, START_DAY)
    # authorTooLongTest(jsonQuotes,START_DAY)

main()
