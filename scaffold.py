# this routine is called if the user details were not in the .forward file.  
# In our environment we can steal them from the Thunderbird control file.  There's a file at:
# C:\Users\<username>\AppData\Roaming\Thunderbird\profiles.ini
# which tells us the location of the Thunderbird profile, in there is a prefs.js file, e.g. at
# C:\Users\<username>\AppData\Roaming\Thunderbird\Profiles\<randomstring>\prefs.js
# and we can read that to get the user full name and the email address.
# another way might be to do an LDAP query.

# todo:
# handle errors, can't read file(s), can't get user details.

import os
import pathlib
import re # so we can use regular expressions

debug = True
# debug = False

# import get_user_details.GetUserDetails as GetUserDetails

from get_user_details import GetUserDetails
# using get_user_details  

MyName  = ""
MyEmail = ""
gotDetail = ""


gotDetail, MyName, MyEmail = GetUserDetails(debug)

# if debug:
print("\nafter function call:")
print("   MyName: \"" + MyName + "\"\n" + \
        "  MyEmail: \"" + MyEmail + "\"")
if gotDetail:
    print("gotDetail: True\n")
else:
    print("gotDetail: false\n")

