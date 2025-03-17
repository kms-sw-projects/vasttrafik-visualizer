**Västtrafik ticket visualizer**
--------------------------------

This project allows for automatic parsing of [Västtrafik](https://www.vasttrafik.se) tickets from emails, and subsequent visualization of the data.

It contains two seperate but connected parts:

1. Email parsing (parseMails.py)
    
    This assumes that you have received payment confirmation emails from Västtrafik when buying a ticket.
    Furthermore, you should move all of those emails into a single subfolder on your mail space. The code assumes this to bo in INBOX/Vasttrafik, 
    but this path can be adjusted. The script will then download all emails and parse them for relevant information (Date, Number of tickets bought, total amount spent).
	As a last step, all this information is put into a pandas database.

2. Data visualization (vasttrafik.py)
    
    The data from the pandas database gets loaded and some visualizations are created to give a better overview.
    This includes yearly spending, monthly spending, averaged spending per day, and some others. This might be growing in the future.
