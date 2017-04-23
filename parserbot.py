from html.parser import HTMLParser
from urllib.request import urlopen
from urllib import parse


class ParserBot(HTMLParser):
    """Simple HTML parser built to extract links and school information from indschools.co.uk"""
    def __init__(self):
        """The self.school_links list stores links to school profiles on the website.
        
        The self.data list stores all the information we are interested in for one school at a time.
        """
        super().__init__()
        self.base_url = ''
        self.school_links = []
        self.data = []
        
        # A switch - are we currently trying to pull links?
        self.getting_school_links = False
        
        # A switch - are we currently trying to pull school data?
        self.getting_school_info = False
        
        # A switch - is the parser currently looking at a label element?
        self.looking_at_label = False
        
        # A switch - have we found the area where the phone number is?
        self.waiting_for_phone = False
        
        # A switch - are we allowing data to be stored at this time?
        self.getting_data = False
        
        # A switch - have we found the area where the age ranges are?
        self.getting_ages = False                   
        
        # A counter - helps us know when to turn off getting_data switch.
        self.counter = 0
        
        # A counter - helps us know when to stop pulling age ranges.
        self.agecounter = 0                         
        
        # A counter - helps us know when to stop expecting phone number.
        self.waitingcounter = 0                     

    def refresh(self):
        """Clear the data we have stored in our 'data' container."""
        self.data = []

    def handle_starttag(self, tag, attrs):
        """Override method in HTMLParser.
        
        If we are currently searching for school links from an area 'homepage', the self.getting_school_links switch will
        be True thanks to the get_school_links() method we called.  This handle_starttag() method will tell the parser to add
        all school links it can see in the area to our self.school_links container.
        
        If we are instead searching for school information (i.e. address etc.) from a school's profile on the website, the
        self.getting_school_info switch will be True thanks to the get_school_info() method we called.  This handle_starttag()
        method will turn on additional switches when it comes accross information we care about (in preparation for scraping).
        """
        
        # 'self.getting_school_links' is switched 'on' to True when we want read the list of schools from an area's homepage
        if self.getting_school_links is True:
            if tag == 'div':
                for (attr_name, value) in attrs:
                    if attr_name == 'onclick':
                        end_part = value.split('location.assign')
                        sub_url = end_part[1][2:-3]
                        full_url = parse.urljoin(self.base_url, sub_url)
                        self.school_links.append(full_url)
        
        # 'self.getting_school_info' is switched 'on' to True when we want read the information held on a school's profile page
        if self.getting_school_info is True:
            if tag == 'h1':
                for (attr_name, value) in attrs:
                    if attr_name == 'class' and 'SchoolNameTitle' in value:
                        self.getting_data = True

            if tag == 'label':
                self.looking_at_label = True

            if tag == 'span':
                for (attr_name, value) in attrs:
                    if attr_name == 'id' and (value == 'CPHBodyContent_UCFee_LblPupil_Boy_Day_AgeRange' or
                                                      value == 'CPHBodyContent_UCFee_LblPupil_Girl_Day_AgeRange'):
                        self.getting_ages = True

    def handle_data(self, data):
        """Override method in HTMLParser.
        
        Tell our parser to add data to our self.data container once all appropriate switches have been turned on.
        """
        if self.getting_school_info is True:        # only need to handle data on info pages
            if self.getting_data is True:
                self.data.append(data)

            if self.waiting_for_phone is True:
                self.data.append(data)

            if self.looking_at_label is True:
                if data == 'Phone':
                    self.waiting_for_phone = True

            if self.getting_ages is True:
                if self.agecounter <= 7:
                    self.data.append(data)
                    self.agecounter += 1
                else:
                    self.getting_ages = False
                    self.agecounter = 0

    def handle_endtag(self, tag):
        """Override method in HTMLParser.
        
        This method decides when to turn switches off (i.e. to False).
        """
        
        # We only need to worry about turning switches off when we're pulling data from a school's profile page.
        if self.getting_school_info is True:
            
            # Use a counter to turn off the self.getting_data switch once we've passed two <div> tags because this
            # marks the end of the address info section.
            if self.getting_data is True:
                if tag == 'div':
                    self.counter += 1
                    if self.counter == 2:
                        self.getting_data = False
                        self.counter = 0

            if self.looking_at_label is True:
                if tag == 'label':
                    self.looking_at_label = False        # We have now passed the label.

            # Use another counter to stop looking for a phone number after we've passed two <div> tags.
            if self.waiting_for_phone is True:
                if tag == 'div':
                    self.waitingcounter += 1
                    if self.waitingcounter == 2:
                        self.waiting_for_phone = False        # We have now passed the phone number.
                        self.waitingcounter = 0

    def get_school_links(self, url):
        """Pull links from an area page"""
        try:
            response = urlopen(url)
        except:
            print('Error opening url ' + url)
            return
        content = response.getheader('Content-Type')
        if content == 'text/html' or content == 'text/html; charset=utf-8':
            html_as_bytes = response.read()
            html_as_string = html_as_bytes.decode('utf-8')
            self.getting_school_links = True
            self.base_url = url
            self.feed(html_as_string)
            print('Fed ' + url + ' to your ParserBot.')
        else:
            print(url + " doesn't contain permitted HTML content type.  Page was not fed to your ParserBot.")
            return

    def get_school_info(self, url):
        """Pull a school's name, address, phone, and ages from its indschools.co.uk page"""
        try:
            response = urlopen(url)
        except:
            print('Error opening url ' + url)
            return
        content = response.getheader('Content-Type')
        if content == 'text/html' or content == 'text/html; charset=utf-8':
            html_as_bytes = response.read()
            html_as_string = html_as_bytes.decode('utf-8')
            self.getting_school_info = True
            self.feed(html_as_string)
            print('Fed ' + url + ' to your ParserBot.')
        else:
            print(url + " doesn't contain permitted HTML content type.  Page was not fed to your ParserBot.")
            return
