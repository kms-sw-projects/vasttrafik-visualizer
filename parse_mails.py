""" A simple program to connect to mail server via IMAP, 
    and iterate through all mails in a given subfolder.
    Extract payment amount, datetime, and number of tickets bought 
    from Vasttrafik ticket payment receipts."""

import imaplib as iml
import email
from email.header import decode_header
from bs4 import BeautifulSoup
import pandas as pd

# Helper function used for text parsing later
def find_ticket_count(order_string):
    """ From an order string, extract the number of tickets bought as an integer."""
    if order_string.find("2 ×") != -1:
        return 2
    if order_string.find("3 ×") != -1:
        return 3
    if order_string.find("4 ×") != -1:
        return 4
    if order_string.find("5 ×") != -1:
        return 5
    if order_string.find("6 ×") != -1:
        return 6
    return 1
# Crate final pandas DataFrame to store data in
df = pd.DataFrame(columns=["datetime", "SEK", "Single tickets bought",
                           "Day", "Month", "Year", "weekday"])
df["datetime"] = pd.to_datetime(df["datetime"], unit="ms")
df["SEK"] = df["SEK"].astype("float32")
df["Single tickets bought"] = df["Single tickets bought"].astype("Int32")
df["Day"] = df["Day"].astype("Int32")
df["Month"] = df["Month"].astype("Int32")
df["Year"] = df["Year"].astype("Int32")

login_name = input("Please specify your login name, e.g. in the form test@side.com: ")
login_password = input("Please specify your email password: ")

with iml.IMAP4_SSL("imap.yourhost.domain", 993) as M:
    # login into email server
    M.login(login_name, login_password)
    # select correct folder
    # return values indicate if it exists and how many emails are to be processed
    status, messages = M.select(mailbox="INBOX/Vasttrafik", readonly=True)
    # convert message count to int number
    messages = int(messages[0])
    # N is the number of messages to be processed.
    # we will iterate in reverse order (high indices) downward
    # The 30 is arbitrary and just a cutoff for "too old" emails (< 2016) that had weird formatting
    N = messages-30
    for num in range(messages, messages-N, -1):
        # fetch email number num
        res, msg = M.fetch(str(num), '(RFC822)')
        # as progress info, print out the current number compared to the total count
        print("Email number ", num, " of ", messages)
        for response in msg:
            if isinstance(response, tuple):
                # parse a bytes email into a message object
                msg = email.message_from_bytes(response[1])
                # extract subject
                subject, encoding = decode_header(msg.get("Subject"))[0]
                if isinstance(subject, bytes):
                    # if it's a bytes, decode to str
                    if encoding is not None:
                        subject = subject.decode(encoding)
                    else:
                        # if no encoding is specified (this happens) just use the actual header info
                        subject = msg.get("Subject")
                From, encoding = decode_header(msg.get("From"))[0]
                if isinstance(From, bytes):
                    if encoding is not None:
                        From = From.decode(encoding)
                    else:
                        # if no encoding is specified (this happens) just use the actual header info
                        From = msg.get("From")
                msg_date, encoding = decode_header(msg.get("Date"))[0]
                if isinstance(msg_date, bytes):
                    if encoding is not None:
                        msg_date = msg_date.decode(encoding)
                    else:
                        # if no encoding is specified (this happens) just use the actual header info
                        msg.get("Date")
            if subject.find("Betalning") != -1:
                if msg.is_multipart():
                    # iterate over email parts
                    for part in msg.walk():
                        # extract content type of email
                        content_type = part.get_content_type()
                        try:
                            # get the email body
                            body = part.get_payload(decode=True).decode()
                        except:
                            pass
                        if content_type == "text/html":
                            # parse the email via BeautifulSoup
                            soup = BeautifulSoup(body, "html.parser")
                            # take stripped strings and store each piece in a long list
                            string_list = []
                            for string in soup.stripped_strings:
                                string_list.append(string)
                            # find the string that contains "Summa betalt"
                            betalt_index = string_list.index("Summa betalt:")
                            # extract the actual amount paid.
                            # Over the years the formats have changed from "X kr", "X SEK", "SEK X"
                            # different cases to handle that
                            money_spent = 0
                            if string_list[betalt_index+1].find("kr") != -1:
                                money_spent = string_list[betalt_index+1]
                                money_spent = money_spent.strip(" ").split("(")[0][0:-3]
                            if string_list[betalt_index+1].find("SEK") == 0:
                                money_spent = string_list[betalt_index+1]
                                money_spent = money_spent.strip(" ").split("(")[0][3:]
                            elif string_list[betalt_index+1].find("SEK") != -1:
                                money_spent = string_list[betalt_index+1]
                                money_spent = money_spent.split("SEK")[0].strip(" ")
                                money_spent = money_spent.replace("\xa0", "")
                            # find the line that contains "din beställning"
                            bestallning_index = string_list.index("Din beställning:")
                            # from this line we can extract the number of tickets bought
                            ticket_count = find_ticket_count(string_list[bestallning_index+1])
                            # add a new entry to the pandas database
                            df.loc[len(df)] = {"datetime": msg_date[5:-6],
                                               "SEK": float(money_spent.replace(",",".")),
                                               "Single tickets bought":ticket_count}
                else:
                    content_type = msg.get_content_type()
                    # get the email body
                    body = msg.get_payload(decode=True).decode()
                    if content_type == "text/html":
                        # parse the email via BeautifulSoup
                        soup = BeautifulSoup(body, "html.parser")
                        # take all text via stripped strings and store all of them in a long list
                        string_list = []
                        for string in soup.stripped_strings:
                            string_list.append(string)
                        # find the string that contains "Summa betalt"
                        betalt_index = string_list.index("Summa betalt:")
                        # extract the actual amount paid.
                        # Over the years the formats have changed from "X kr", "X SEK", "SEK X"
                        # different cases to handle that
                        money_spent = 0
                        if string_list[betalt_index+1].find("kr") != -1:
                            money_spent = string_list[betalt_index+1]
                            money_spent = money_spent.strip(" ").split("(")[0][0:-3]
                        if string_list[betalt_index+1].find("SEK") == 0:
                            money_spent = string_list[betalt_index+1]
                            money_spent = money_spent.strip(" ").split("(")[0][3:]
                        elif string_list[betalt_index+1].find("SEK") != -1:
                            money_spent = string_list[betalt_index+1]
                            money_spent = money_spent.split("SEK")[0].strip(" ")
                            money_spent = money_spent.replace("\xa0", "")
                        # find the line that contains "din beställning"
                        bestallning_index = string_list.index("Din beställning:")
                        # from this line we can extract the number of tickets bought
                        ticket_count = find_ticket_count(string_list[bestallning_index+1])
                        # add a new entry to the pandas database
                        df.loc[len(df)] = {"datetime": msg_date[5:-6],
                                           "SEK": float(money_spent.replace(",",".")),
                                           "Single tickets bought":ticket_count}
    # Logout of the email server
    print(M.logout())
# add so additional columns to the database and format the date to datetime
df["datetime"] = pd.to_datetime(df["datetime"],format="%d %b %Y %H:%M:%S")
df["Day"] = df["datetime"].dt.day
df["Month"] = df["datetime"].dt.month
df["Year"] = df["datetime"].dt.year
df["weekday"] = df["datetime"].dt.weekday
# print some DB info and head
print(df.info())
print(df.head())
# save database to file
df.to_csv("./tickets_automated.csv")
