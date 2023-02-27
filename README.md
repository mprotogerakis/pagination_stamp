# pagination_stamp
For use with the PDF Archiver (https://apps.apple.com/de/app/pdf-archiver-1/id1352719750?mt=12) I created a small helper for further post processing after the use of the macos app.

pagination_stamp is a python script of macos that is engaged by context menu through automator

<img width="778" alt="image" src="https://user-images.githubusercontent.com/16209932/221431258-dc6cd908-4913-47fc-bc0d-51712cd92719.png">

it receives a directory as commadn line argument. that directory contains a lot of pdfs according to the scheme
  yyyy-mm-dd--some-description-with-no-whitespaces-and-underscores__tag1_tag2_tagx.pdf
and an ini file pagination.ini with the following content:
~~~
      [directory]
      file_counter_start = 20230000
      mac_set_file_creation_dates = yes
      stamp_file_counter = yes
      stamp_file_name = yes
      macos_tags = yes
      regex_pagination = ((_rechnung)|(steuer)|(beleg))
      create_excel = yes
      excel_filename = Belege2023.xlsx
~~~
The script will go through all the files and 
  - set file creation dates according to the date in the filename (if configured via mac_set_file_creation_dates)
  - set macos tags to match the tags in the file name (if configured via macos_tags)
  - add a pagination number to the filename if it matches the regex_pagination.
      - add this spagination number to the first page if configured via stamp_file_counter
      - add the filename to the first page if configured via stamp_file_name
  - create an excel list of the paginated files (excel_filename) in the directory if configured via create_excel
