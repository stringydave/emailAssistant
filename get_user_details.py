# this routine is called if the user details were not in the .forward file.  
# In our environment we can steal them from the Thunderbird control file.  There's a file at:
# C:\Users\<username>\appdata\Roaming\Thunderbird\profiles.ini
# which tells us the location of the Thunderbird profile, in there is a prefs.js file, e.g. at
# C:\Users\<username>\appdata\Roaming\Thunderbird\Profiles\<randomstring>\prefs.js
# and we can read that to get the user full name and the email address.
# another way might be to do an LDAP query.

# todo:
# handle errors, can't read file(s), can't get user details.

import os
import pathlib
import re # so we can use regular expressions


def GetUserDetails(debug=False):

    if debug:
        print("\nGetUserDetails from Thunderbird prefs file...")

    home_share          = os.getenv('HOMESHARE')
    system_drive        = os.getenv('SYSTEMDRIVE')
    appdata             = os.getenv('APPDATA')

    # we need these things
    Thunderbirdini      = appdata + "\Thunderbird\profiles.ini"

    # read the ini file, it contains text like:
    # isRelative=1
    # Path=Profiles/randomstring
    # Default=1

    if debug:
        print("\n  reading:", Thunderbirdini)

    try: 
        with open(Thunderbirdini, 'r') as f:
            Thunderbirdini_file = [line.rstrip() for line in f]
    except Exception as error:
        # we couldn't open the file for some reason
        if debug:
            print(error)
        return False,"",""

    # now read the list we have until we find the one which says "Default=1"
    for i in range(0, len(Thunderbirdini_file), 1):
        this_line = Thunderbirdini_file[i]

        if re.search('(?i)isRelative',this_line):
            if debug:
                print(".ini file:", this_line)
            this_line_split = this_line.split('=')
            isRelative = this_line_split[len(this_line_split) - 1]
        if re.search('(?i)Path',this_line): 
            if debug:
                print(".ini file:", this_line)
            this_line_split = this_line.split('=')
            Path = this_line_split[len(this_line_split) - 1]
        if re.search('(?i)Default',this_line):
            if debug:
                print(".ini file:", this_line)
            this_line_split = this_line.split('=')
            isDefault = this_line_split[len(this_line_split) - 1]
            if re.search('1',isDefault):
                break
        
    if debug:
        print( "isRelativ:", isRelative + \
             "\n     Path:", Path + \
             "\nisDefault:", isDefault + "\n")

    # if we haven't found default, then give up
    if isDefault != "1":
        return False, "", ""

    # now we've found out where the Profile is, we need to read the prefs.js file, work out where it is
    if isRelative == "1": 
        ThunderbirdPrefs = appdata + "\\Thunderbird\\" + Path + "\\prefs.js"
    else:
        ThunderbirdPrefs = Path + "\\prefs.js"

    # turn the separators round the right way
    ThunderbirdPrefs = ThunderbirdPrefs.replace("/","\\")
        
    # now we've found out where the active Profile is, we need to read the prefs.js file, and find these lines
    # user_pref("mail.identity.id1.fullName", "Firstname Secondname");
    # user_pref("mail.identity.id1.useremail", "user.name@company.com");
    # there may be other id2,3,4 identities, but they will be for other services, and not useful to our quest

    if debug:
        print("  reading:", ThunderbirdPrefs)

    try: 
        with open(ThunderbirdPrefs, 'r') as f:
            ThunderbirdPrefs_file = [line.rstrip() for line in f]
    except Exception as error:
        # we couldn't open the file for some reason
        if debug:
            print(error)
        return False, "", ""

    # now read the list we have until we find the ones which contain "mail.identity.id1"
    for i in range(0, len(ThunderbirdPrefs_file), 1):
        this_line = ThunderbirdPrefs_file[i]
        if re.search('(?i)mail.identity.id1.fullName',this_line):
            # if debug:
            #     print(this_line)
            this_line_split = this_line.split(',')
            MyName = this_line_split[len(this_line_split) - 1]
        if re.search('(?i)mail.identity.id1.useremail',this_line): 
            # if debug:
            #     print(this_line)
            this_line_split = this_line.split(',')
            MyEmail = this_line_split[len(this_line_split) - 1]
        
    # clean up the variables
    MyName  = MyName.replace("\"","")
    MyName  = MyName.replace(");","")
    MyName  = MyName.strip()
    MyEmail = MyEmail.replace("\"","")
    MyEmail = MyEmail.replace(");","")
    MyEmail = MyEmail.strip()

    # if we've got this far the worst that can happen is that we failed to extract a meaningful name and email address
    # so let's just pass back what we've got

    if debug:
        print("   MyName: \"" + MyName + "\"\n" + \
          "  MyEmail: \"" + MyEmail + "\"")

    return True, MyName, MyEmail



