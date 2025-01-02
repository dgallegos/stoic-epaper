
import sys
import json

### 
## Quote Model
###
class Quote():
    date = None
    title = None
    quote = None
    author = None
    commentary = None

    def __init__(self,date,title,quote,author,commentary):
        self.date = date
        self.title = title
        self.quote = quote
        self.author = author
        self.commentary = commentary

    @staticmethod
    def GetQuotesFromFile(filename):
        try:
            with open(filename, 'r') as f:
                # Load the JSON data into a Python object
                quotesJson = json.load(f)
                quotes = [Quote(item['date'], item['title'], item['quote'], item['author'], item['commentary']) for item in quotesJson]
                return quotes
        except FileNotFoundError:
            print("File not found: " + filename)
            sys.exit(1)
    
    def display(self):
        print("title:" + self.title + "\n")
        print("quote:" + self.quote + "\n")
        print("author:" + self.author + "\n")
        print("date:" + self.date + "\n")
        
        