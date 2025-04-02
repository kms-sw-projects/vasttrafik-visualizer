""" A helper funciton module for Västtrafik ticket visualization."""
def monthyear_from_number(number, monthslist, start_year, start_month):
    """Convert a Year-Month index number to a string of form 'Month-Year' (%b-%Y format datetime)"""
    year = start_year + math.floor((number+start_month)/12)
    month = monthslist[ (number+start_month) % 12]
    return str(month)+" "+ str(year)

def year_from_monthyear(monthyear, month, start_year, start_month):
    """Convert a Year-Month index number to a year Integer."""
    actual_year = np.floor( (monthyear - (month-start_month) )/12) + start_year
    return actual_year

def month_from_monthyear(monthyear, year, start_year, start_month):
    """Convert a Year-Month index number to a month Integer."""
    actual_month = monthyear - 12*(year -start_year) + start_month
    return actual_month

def read_ticket_data(filename_pass):
    """ Read a CSV file created by parse_mail 
        into a pandas dataframe and change some aspects of it.
        Input: filename_pass, string - absolute or relative path to the csv file.
    
        Returns: Pandas DataFrame containing the data."""
    # Read CSV file
    df = pd.read_csv(filename_pass, header=0)
    df['SEK'] = df['SEK'].fillna(0)
    df.head()
    # change date column datatype to datetime
    df['datetime'] = pd.to_datetime(df['datetime'])
    # remove duplicate entries
    df.drop_duplicates("datetime", inplace=True)
    # set datetime column as index
    df.set_index("datetime", inplace=True)
    # drop unnecessary old index
    df.drop("Unnamed: 0", axis=1, inplace=True)
    # show start of the data
    df.head(100)
    return df