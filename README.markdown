SMS (Sms Management Suite )
==========================

Manager for mobile messages in computer. Takes .vmg messages as input and converts them to single-file nice-looking conversation per contact. Output file format is html, so can be viewed across all operating systems and browsers (including mobile!).

Details
-------
Currently supports only text messages stored as `.vmg` files. These messages can be exported from phone using Nokia PC Suite, or can be extracted from backup using NBUexplorer application (an open source application hosted on SourceForge). 
Example output conversation file can be found <a href="http://dl.dropbox.com/u/42084476/Extra/9987114106_2012.html" target="_blank">here</a>.

Requirements
------------
1. A Linux machine with Python installed on it (2.4+)

How to use
----------

    ./src/smsInit.py

This will create `to_process`, `processed`, `meta`, `conversations` and `unprocessed` directories. You need to put all your .vmg files in `to_process` folder. All the processed vmg files will be moved to `processed` folder after processing. All the output conversation html files will go into `conversations` folder. Then execute:

    ./src/sms.py

And you are done! Check `conversations` folder to see the conversation files.

Contributing
------------
Want to contribute? Great! Contact me at `rushi.agr@gmail.com`. Here is the list of things I want to develop:

Issues and Future Development
-----------------------------

Current development is halted, as my old Laptops's harddisk crashed, and I changed my phone to Android :)

Future development in the increasing order of time required:

1. Using shadows in the output html file. Enhancing the colour scheme.
2. Support for Samsung, LG, Android, etc messages
3. Cross-platform application (specifically Windows)
4. Develop a cool GUI for the application (preferably in GTK)
5. Develop message viewing/scrolling/finding/selectively saving abilities in the GUI.
6. Develop python independent binary executables (using PyGtk, PyInstaller or something similar).
