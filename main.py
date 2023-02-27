import PyPDF2
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import red
import os.path
import datetime
import configparser
from pathlib import Path
import sys
import macos_tags
import os
import re
import datetime
import pandas as pd


def mac_set_file_creation_date(year, month, day, full_filepath):
    file_date_to_be_set = datetime.datetime(year, month, day, 0, 0, 0)
    os.system('SetFile -d "{}" {}'.format(file_date_to_be_set.strftime('%m/%d/%Y %H:%M:%S'), full_filepath))


def create_stamp_page_filename(text):
    local_packet = io.BytesIO()
    local_can = canvas.Canvas(local_packet, pagesize=A4)
    local_can.setFont("Helvetica", 8)
    local_can.setFillColor(red)
    local_can.drawString(10, 10, text)
    local_can.save()
    local_new_pdf_page = PyPDF2.PdfReader(local_packet)
    return local_new_pdf_page


def create_stamp_page_file_counter(text):
    local_packet = io.BytesIO()
    local_can = canvas.Canvas(local_packet, pagesize=A4)
    local_can.setFont("Helvetica", 14)
    local_can.setFillColor(red)
    local_can.drawString(450, 800, text)
    local_can.save()
    local_new_pdf_page = PyPDF2.PdfReader(local_packet)
    return local_new_pdf_page


def remove_extension(file_name):
    return file_name.rsplit('.', 1)[0]


def find_max_pagination_number(local_path):
    # find out maximum used file_counter so far in this directory
    global filename
    local_file_counter = 0
    for filename in os.listdir(local_path):
        if filename.endswith(".pdf"):
            local_pattern = re.compile(r'(\d+)#_(\d{4})-(\d{2})-(\d{2})--.*')
            # those have already been processed
            local_match = re.search(local_pattern, filename)
            if local_match:
                number = int(local_match.group(1))
                if number > local_file_counter:
                    local_file_counter = number
    if local_file_counter == 0:
        local_file_counter = int(config['directory']['file_counter_start'])
    local_file_counter = local_file_counter + 1
    return local_file_counter


if not (len(sys.argv) == 2):
    raise Exception("Please provide a directory path as a command line argument." + str(len(sys.argv)))

path = sys.argv[1]

my_dir = Path(path)
if my_dir.is_dir():
    config_file = path + "/pagination.ini"
    my_config_file = Path(config_file)
    if not my_config_file.is_file():
        raise Exception("Directory does not contain a pagination.ini file.")
else:
    raise Exception("Command line argument is not a directory.")

config = configparser.ConfigParser()
config.read(config_file)

file_counter = find_max_pagination_number(path)


def regex_matches(regex, local_filename):
    local_pattern = re.compile(regex)
    # those have already been processed will match
    return re.search(local_pattern, local_filename)


for filename in os.listdir(path):
    if filename.endswith(".pdf"):
        match_paginated_before = regex_matches(r'(\d+)#_(\d{4})-(\d{2})-(\d{2})--.*', filename)
        if match_paginated_before:
            # those have been paginated before
            # re-set the file creation date, do nothing else
            if config.getboolean('directory', 'mac_set_file_creation_dates'):
                mac_set_file_creation_date(int(match_paginated_before.group(2)), int(match_paginated_before.group(3)),
                                           int(match_paginated_before.group(4)), path + "/" + filename)
        else:
            # those have not been paginated before
            match_valid_date = regex_matches(r"(\d{4})-(\d{2})-(\d{2}).*"+str(config['directory']['regex_pagination'])+
                                             ".*", filename)
            if match_valid_date:
                # those have not been paginated before but contain a valid date scheme and one of the terms that
                # allow  paginating (_rechnung)|(steuer)|(beleg)
                print("Paginating " + filename)
                original_pdf_file = open(path + "/" + filename, "rb")
                original_pdf_reader = PyPDF2.PdfReader(original_pdf_file, strict=False)
                new_pdf_writer = PyPDF2.PdfWriter()
                original_page = original_pdf_reader.pages[0]
                # don't know what that was for...
                #original_page.merge_page(original_pdf_reader.pages[0])
                original_page.compress_content_streams()

                # add first stamp to the page
                if config.getboolean('directory', 'stamp_file_name'):
                    filename_stamp_pdf_page = create_stamp_page_filename(str(file_counter) + "#_" +
                                                                         remove_extension(filename) + ".pdf")
                    original_page.merge_page(filename_stamp_pdf_page.pages[0])

                # add second stamp to the page
                if config.getboolean('directory', 'stamp_file_counter'):
                    file_counter_stamp_pdf_page = create_stamp_page_file_counter(str(file_counter))
                    original_page.merge_page(file_counter_stamp_pdf_page.pages[0])

                # add page to the new pdf
                new_pdf_writer.add_page(original_page)

                for i in range(1, len(original_pdf_reader.pages)):
                    # copy all other pages from old pdf to new pdf
                    original_page = original_pdf_reader.pages[i]
                    new_pdf_writer.add_page(original_page)

                os.remove(path + "/" + filename)
                output_file = open(path + "/" + str(file_counter) + "#_" + remove_extension(filename) + ".pdf",
                                   "wb")
                new_pdf_writer.write(output_file)
                original_pdf_file.close()
                output_file.close()
                if config.getboolean('directory', 'mac_set_file_creation_dates'):
                    mac_set_file_creation_date(int(match_valid_date.group(1)),
                                               int(match_valid_date.group(2)),
                                               int(match_valid_date.group(3)), path + "/" + str(file_counter) +
                                               "#_" + remove_extension(filename) + ".pdf")
                file_counter += 1
            else:
                # process those files that have not been matched before but have a valid date in the filename
                match_valid_date = regex_matches(r"(\d{4})-(\d{2})-(\d{2}).*", filename)
                if match_valid_date:
                    # re-set the file creation date
                    if config.getboolean('directory', 'mac_set_file_creation_dates'):
                        mac_set_file_creation_date(int(match_valid_date.group(1)),
                                                   int(match_valid_date.group(2)),
                                                   int(match_valid_date.group(3)), path + "/" + filename)
# rewriting macos tags to all pdf files in directory from file name
for filename in os.listdir(path):
    if filename.endswith(".pdf"):
        if config.getboolean('directory', 'macos_tags'):
            # for all pdf file add macos tags
            tags = remove_extension(filename).split("__")[1].split("_")
            macos_tags.remove_all(path + "/" + filename)
            for tag in tags:
                macos_tags.add(tag, file=path + "/" + filename)

if config.getboolean('directory', 'create_excel'):
    # create empty dataframe to store the extracted information
    df = pd.DataFrame(columns=['date', 'number'])

    # loop through all already paginated pdf files in directory
    for pdf_file in os.listdir(path):
        if pdf_file.endswith('.pdf'):
            # extract date and number from filename
            # regular expression pattern to extract date and number from filename
            pattern = re.compile(r'(\d+)#_(\d{4})-(\d{2})-(\d{2})--(.*)__(.*)')
            match = re.search(pattern, remove_extension(pdf_file))
            if match:
                date_str = f"{match.group(2)}-{match.group(3)}-{match.group(4)}"
                date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
                title = match.group(5)
                tags = match.group(6)
                number = match.group(1)
                # add extracted information to dataframe
                df_new_row = pd.DataFrame({'date': date, 'number': number, 'title': title, 'tags':  tags,
                                           'file': pdf_file}, index=[0])
                df = pd.concat([df, df_new_row])

    # write dataframe to excel file
    df.to_excel(path + "/" + config['directory']['excel_filename'], index=False)
