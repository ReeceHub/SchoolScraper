from parserbot import *
from tkinter import *
import csv


def process(raw):       # outputs a dictionary
    processed = []
    for item in raw:
        if item[0] != '\r':
            processed.append(item)
    processed.append(raw[-17][34:46])

    if len(processed) == 13:
        dictn = {'School Name': processed[0],
                 'Address line 1': processed[1],
                 'Address line 2': processed[2],
                 'Address line 3': processed[3],
                 'Postcode': processed[4],
                 'Country': processed[5],
                 'Number of Boys (day)': processed[6],
                 'Number of Boys (weekly board)': processed[7],
                 'Number of Boys (full board)': processed[8],
                 'Number of Girls (day)': processed[9],
                 'Number of Girls (weekly board)': processed[10],
                 'Number of Girls (full board)': processed[11],
                 'Phone Number': processed[12]
                 }
    elif len(processed) == 12:
        dictn = {'School Name': processed[0],
                 'Address line 1': processed[1],
                 'Address line 2': processed[2],
                 'Address line 3': '',
                 'Postcode': processed[3],
                 'Country': processed[4],
                 'Number of Boys (day)': processed[5],
                 'Number of Boys (weekly board)': processed[6],
                 'Number of Boys (full board)': processed[7],
                 'Number of Girls (day)': processed[8],
                 'Number of Girls (weekly board)': processed[9],
                 'Number of Girls (full board)': processed[10],
                 'Phone Number': processed[11]
                 }
    elif len(processed) == 11:
        dictn = {'School Name': processed[0],
                 'Address line 1': processed[1],
                 'Address line 2': '',
                 'Address line 3': '',
                 'Postcode': processed[2],
                 'Country': processed[3],
                 'Number of Boys (day)': processed[4],
                 'Number of Boys (weekly board)': processed[5],
                 'Number of Boys (full board)': processed[6],
                 'Number of Girls (day)': processed[7],
                 'Number of Girls (weekly board)': processed[8],
                 'Number of Girls (full board)': processed[9],
                 'Phone Number': processed[10]
                 }
    else:
        print("Error in formatting these results.  Too much / too little data.")
        gui.set_status("Error in formatting these results.  Too much / too little data.")
        return
    return dictn


def run_main():
    myparserbot = ParserBot()
    gui.set_status('Visiting school pages and writing data to file.  Please wait; this may take a few moments.')
    myparserbot.get_school_links('http://www.indschools.co.uk/search/list/within/3miles/from/' + gui.postcode)

    if not myparserbot.school_links:      # if we didn't find any links, don't make a file - just exit
        print('No schools found for this postcode.  Exiting program.')
        gui.set_status('No schools found for this postcode.  Please close this dialog box to exit.')
        return
    else:
        with open(gui.file_name + '.csv', 'w', newline='') as myfile:
            field_names = ['School Name', 'Address line 1', 'Address line 2', 'Address line 3', 'Postcode', 'Country',
                           'Number of Boys (day)', 'Number of Boys (weekly board)', 'Number of Boys (full board)',
                           'Number of Girls (day)', 'Number of Girls (weekly board)', 'Number of Girls (full board)',
                           'Phone Number']
            mywriter = csv.DictWriter(myfile, fieldnames=field_names)
            mywriter.writeheader()
            for school in myparserbot.school_links:
                myparserbot.refresh()
                myparserbot.get_school_info(school)
                mywriter.writerow(process(myparserbot.data))
            gui.set_status('Finished writing data to file.  Please close this dialog box to exit.')


class SimpleGui(Tk):
    def __init__(self, name):
        Tk.__init__(self)
        self.title(name)
        self.text1 = Label(self, text='Postcode:')
        self.text1.grid(row=0, column=0, padx=5)
        self.entry1 = Entry(self)
        self.entry1.grid(row=0, column=1, padx=5)
        self.text2 = Label(self, text='File name:')
        self.text2.grid(row=0, column=2, padx=5)
        self.entry2 = Entry(self)
        self.entry2.grid(row=0, column=3, padx=5)
        self.button1 = Button(self, text='Scrape', command=self.call_main)
        self.button1.grid(row=0, column=4, padx=5)
        self.file_name = None
        self.postcode = None
        self.status_text = StringVar()
        self.status_bar = Label(self, textvariable=self.status_text, bd=1, relief=SUNKEN)
        self.status_bar.grid(row=1, columnspan=5, sticky=W+E)

    def call_main(self):
        self.file_name = self.entry2.get()
        self.postcode = self.entry1.get()
        run_main()

    def set_status(self, text):
        self.status_text.set(text)
        self.update_idletasks()

if __name__ == "__main__":
    gui = SimpleGui('School Scraper')
    gui.mainloop()
