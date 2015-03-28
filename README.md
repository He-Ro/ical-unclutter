#iCal-Unclutter
    usage: ical-unclutter.py [-h] [-o OUTPUT] INPUT
    
    Refactor ical files.
    
    positional arguments:
      INPUT                 iCal file that needs uncluttering
    
    optional arguments:
      -h, --help            show this help message and exit
      -o OUTPUT, --output OUTPUT
                            refactored ical file (default: stdout)

Group similar events in the given iCal-Calendar into one unified event.
Two events are similar, if the following values are the same:

-   Summary
-   Description
-   Class
-   Location
-   Categories
-   Start- and Endtime

##Dependencies

-   Python
-   icalendar (AUR: python-icalendar-git)
