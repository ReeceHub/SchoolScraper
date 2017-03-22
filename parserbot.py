from html.parser import HTMLParser
from urllib.request import urlopen
from urllib import parse


class ParserBot(HTMLParser):
    def __init__(self):
        super().__init__()
        self.base_url = ''
        self.school_links = []
        self.data = []

        self.getting_school_links = False           # a switch - are we currently trying to pull links?
        self.getting_school_info = False            # a switch - are we currently trying to pull school data?
        self.looking_at_label = False               # a switch - is the ParserBot currently looking at a label element?
        self.waiting_for_phone = False              # a switch - have we found the area where the phone number is?
        self.getting_data = False                   # a switch - are we allowing data to be stored at this time?
        self.getting_ages = False                   # a switch - have we found the area where the age ranges are?

        self.counter = 0                            # a counter - helps us know when to turn off getting_data switch
        self.agecounter = 0                         # a counter - helps us know when to stop pulling age ranges
        self.waitingcounter = 0                     # a counter - helps us know when to stop expecting phone number

    def refresh(self):
        self.data = []

    def handle_starttag(self, tag, attrs):
        if self.getting_school_links is True:   # reading 'homepage' list
            if tag == 'div':
                for (attr_name, value) in attrs:
                    if attr_name == 'onclick':
                        end_part = value.split('location.assign')
                        sub_url = end_part[1][2:-3]
                        full_url = parse.urljoin(self.base_url, sub_url)
                        self.school_links.append(full_url)

        if self.getting_school_info is True:    # reading a school info page
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
        if self.getting_school_info is True:        # only need to worry about turning the data switch off...
            if self.getting_data is True:           # ...if we're trying to pull info from the page
                if tag == 'div':
                    self.counter += 1
                    if self.counter == 2:
                        self.getting_data = False
                        self.counter = 0

            if self.looking_at_label is True:
                if tag == 'label':
                    self.looking_at_label = False       # finished looking at a label

            if self.waiting_for_phone is True:
                if tag == 'div':
                    self.waitingcounter += 1
                    if self.waitingcounter == 2:
                        self.waiting_for_phone = False      # we've now passed the phone number
                        self.waitingcounter = 0

    def get_school_links(self, url):    # pull links from area page
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

    def get_school_info(self, url):     # pull school's name, address, phone, ages from its indschools.co.uk page
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
