'''
We want to do several things with this file, any one of:
1. copy all inbound mail to another user (optionally don't copy to myself) - OR
2. set an Out of Office (Vacation) message - OR
3. turn off both of the above

to do this we will need to read and write a .forward file in the user's home area together with a vacation file for a vacation message
https://www.exim.org/exim-html-current/doc/html/spec_html/filter_ch-exim_filter_files.html

'''

import re # so we can use regular expressions
import PySimpleGUI as sg
import os
import pathlib
# import os.path

from control_file import control_file_read
from control_file import control_file_write

# sg.theme('Dark Red')
# sg.theme('Default1')
# sg.set_options(text_color='black', background_color='#A6B2BE', text_element_background_color='#A6B2BE')
# ------ Menu Definition ------ #
# menu_def = [['&File', ['&Open', '&Save', 'E&xit', 'Properties']],
            # ['&Edit', ['Paste', ['Special', 'Normal', ], 'Undo'], ],
            # ['&Help', '&About...'], ]

##########################################################################
# define Global variables, this is bad form, we should try not to do this
##########################################################################

# we need to find out where the control files will be
# ideally HOMESHARE=\\server.address\usershare, but sometimes that's not defined
# USERPROFILE=C:\Users\username, which is no use, we can use
# HOMEDRIVE=H: & HOMEPATH=\ 
# but sometimes they're set to HOMEDRIVE=C: & HOMEPATH=\Users\username, which is no use at all
# and LOGONSERVER=\\a-server-on-the-network but it might not be the one where the shares are
# so as a backup, we probably want to do some combination of 
# net use, look for a share with username in it, and use that.
# H:        \\server.address\usernameshare

# initialise GLOBAL
debug = False
home_share          = os.getenv('HOMESHARE')
system_drive        = os.getenv('SYSTEMDRIVE')
vacation_section = False
vacation_section_start = 0
vacation_section_end = 0
alias_index = 0
alias_list = ""
my_name = ""
# define empty lists
control_file = [""]
control_file.clear()
alias_list = ["aliases"]
alias_list.clear()
vacation_file = [""]
vacation_file.clear()
# email_address = ""

debug = True

if debug:
    control_file_path   = ".forward"
    vacation_file_path  = ".vacation.msg"
else:
    control_file_path   = home_share + "\.forward"         # this is required
    vacation_file_path  = home_share + "\.vacation.msg"    # this is the default, can be overridden

# the pathlib library allows us to do path operations whilst taking care of how the underlying operating system wants it
control_template    =  pathlib.Path(__file__).parent.absolute() / "forward.template"
vacation_template   =  pathlib.Path(__file__).parent.absolute() / "vacation.template"

debug = False

if debug:
    print("     home:", home_share, "\n    drive:", system_drive, "\n .forward:", control_file_path, "\n.vacation:", vacation_file_path)
    print("control_t:", control_template, "\nvacationt:", vacation_template)

''' functions =================================================================
'''

def valid_email(check_email_address):
    # the purpose of this function is to check that a string looks like a valid email address
    # https://stackoverflow.com/questions/8022530/how-to-check-for-valid-email-address
    # check that it seems valid and that it's not still the default address with which we're populating the form
    if len(check_email_address) > 10 \
        and bool(re.search(r"^[\w\.\+\-]+\@[\w]+\.[a-z]{2,3}$", check_email_address)) \
        and not re.search("ecipient", check_email_address) \
        and not re.search("company",  check_email_address):
        return True
    else:
        return False

# from collections import namedtuple
# https://book.pythontips.com/en/latest/global_&_return.html
def get_user_details():
    # called if the user details were not in the .forward file.  In our environment we can steal them from the 
    # Thunderbird control file.  There's a file at:
    # C:\Users\username\AppData\Roaming\Thunderbird\profiles.ini
    # which tells us the location of the Thunderbird profile, in there is a prefs.js file, e.g. at
    # C:\Users\username\AppData\Roaming\Thunderbird\Profiles\randoming\prefs.js
    # and we can read that to get the user full name and the email address.
    # another way might be to do an LDAP query.
    
    # for now, skeleton
    # user_details = namedtuple('user_details', 'fullname user_email' )
    # return user_details(fullname="My Name", user_email="recipient@company.com")
    fullname="My Name"
    user_email="recipient@company.com"
    return fullname, user_email

def set_redirect(set_this, redirect_to = 'dummy@dummy.com'):
# if we're called with true, then 
    if debug:
        print('  set_redirect: ', set_this, redirect_to)
    if set_this:
        if valid_email(redirect_to):
            control_file[forward_line] = "unseen deliver " + redirect_to
            # and turn off any Vacation message
            set_vacation(False)
            # and write the control file
            cf_write_status = control_file_write(control_file, control_file_path, debug)
            return cf_write_status
        else:
            sg.popup('send a copy email address:' + redirect_to, 'does not seem to be a valid email address', title = 'error')
            return False
    else: 
        # add a comment to the start of the line, unless it already has one
        if not re.match("#", control_file[forward_line]):
            control_file[forward_line] = "# " + control_file[forward_line]
        # and write the control file
        cf_write_status = control_file_write(control_file, control_file_path, debug)
        return cf_write_status

def set_vacation(set_this, vacation_my_name="", vacation_my_aliases="", vacation_message=""):
    global vacation_section_end
    if debug:
        print('  set_vacation: ', set_this, vacation_my_name, vacation_my_aliases, vacation_message)
        print('vacation_start: ', vacation_section_start)
        print('  vacation_end: ', vacation_section_end)
    if set_this:
        # the variable vacation_file_linux_version is set already
        
        # update the variables
        if len(vacation_my_name) < 3:
            sg.popup('out of office "my name"' + vacation_my_name, ' does not seem to be valid', title = 'error')
            return False
        
        # vacation_my_aliases is potentially a multiline string
        # remove any trailing \n
        vacation_my_aliases = re.sub("\n$", "", vacation_my_aliases)
        # split on \n
        aliases = re.split(r"\n+", vacation_my_aliases)
        # and parse the email aliases
        for i in range(0, len(aliases), 1):
            if not valid_email(aliases[i]):
                sg.popup('my email address: ' + aliases[i], "does not seem to be a valid email address", title = 'error')
                return False

                # Msgbox "out of office ""my email address""" & vbCRLF & EmailAddressRead(i) & vbCRLF & "does not seem to be a valid email address"
                # SetVacationStatus = False
                # Exit Sub
            # Else
                # EmailAddressWrite(i) = "  alias " & EmailAddressRead(i)
            # End if
        # Next
        
        # this is the from line: from "Firstname Secondname <recipient.name@company.co.uk>"
        control_file[vacation_from_line]  = '  from "' + vacation_my_name + ' <' + aliases[0] + '>"'
        if debug:
            print("     aliases:", len(aliases), aliases)
        
        # and we need to deal with the alias lines:
        # alias recipient.name@company.co.uk"
        # and there could be more or less of them than we had in the file we just read.
        # when we read the control file there were intAliasIndex alias lines, (which we assume are contiguous)
        # and now there are Ubound(EmailAddressRead) alias lines
        # so we're going to overwrite lines from 
        #   EmailAddressLines(0)
        # to
        #   EmailAddressLines(Ubound(EmailAddressRead))
        
        # so shuffle everything in the right direction
        # intShuffleAmount = intAliasIndexRead - intAliasIndex 
        # For i = intControlFileEOF to EmailAddressLines(0) + intAliasIndex step -1
            # control_file(i + intShuffleAmount) = control_file(i)
        # Next
        
        
        # For i = 0 to intAliasIndexRead - 1
            # # if this is empty or does not look like an email address, fill it with default
            # if valid_email(EmailAddress(i)): EmailAddress(i) = EmailAddress(0)
            # control_file(EmailAddressLines(i)) = "  alias " & EmailAddress(i)
        # Next

        # so by now we've got everything back into the list, we just need to uncomment as required
        control_file[vacation_section_start] = re.sub(r"^# *", "", control_file[vacation_section_start])
        # an obscurity of python for loops is that the "to" part stops 1 before the end, so this will stop before the last line, which is what we want.
        for j in range(vacation_section_start, vacation_section_end, 1):
            # str.replace doesn't handle regular expressions, so use re.sub, we want 2 spaces
            control_file[j] = re.sub("^# *", "  ", control_file[j])
        # and then do the last line of the section
        control_file[vacation_section_end] = re.sub("^# *", "", control_file[vacation_section_end])
        
        if debug:
            for j in range(vacation_section_start, vacation_section_end + 1, 1):
                print(control_file[j])
        # and do this
        set_redirect(False)

        # # write out the vacation file in case we changed it
        # Set VacationFile = fso.OpenTextFile(VacationFile, ForWriting, True)
        # VacationFile.Write(VacationMessage.Value)
        # Msgbox _
            # "Out of Office message set:" & vbCRLF & vbCRLF & _
            # "From: " & vacation_my_name & " " & EmailAddress(0) & vbCRLF & _
            # "Subject: Auto: Re: <message_subject>" & vbCRLF & _
            # "Message: " & VacationMessage.Value & vbCRLF & vbCRLF& _
            # "Please remember to turn this off on your return"
        return True
    else: 
        # add a comment to the start of the line, unless it already has one
        for j in range(vacation_section_start, vacation_section_end + 1, 1):
            if not re.match("#", control_file[j]):
                control_file[j] = "# " + control_file[j]
            if debug:
                print(control_file[j])
        return True

def reset():
    # turn off Redirect and Vacation
    if debug:
        print('  called reset: ')
    redirect_unset = set_redirect(False)
    vacation_unset = set_vacation(False)
    if debug:
        print('  called reset: ', redirect_unset, vacation_unset)
    return (redirect_unset and vacation_unset )


''' end functions, start of work ################################################
'''

# read the control file & vacation file
# let the user manipulate the relevant sections
# write the files out again

# read the control file into a list
if not control_file_read(control_file, control_file_path, debug):
    # failed to read the control file, try the template
    if not control_file_read(control_file, control_template, debug):
        # template failed as well, tell the user
        # Popup(args=*<1 or N object>, title=None, button_color=None, background_color=None, text_color=None, button_type=0, auto_close=False, auto_close_duration=None, custom_text=(None, None), non_blocking=False, icon=None, line_width=None, font=None, no_titlebar=False, grab_anywhere=False, keep_on_top=False, location=(None, None))
        sg.popup('Required file(s) missing' + \
            '\n  failed to read control file:\t' + str(control_file_path) + \
            '\n  failed to read template file:\t' + str(control_template) +\
            '\nPlease report this error, program will now exit', title = "Error")
        exit()

if debug:
    print("control file ======================================================")
    for i in range(0, len(control_file), 1):
        print(str(i) + ":", control_file[i])

''' parse the control file ===============================================
'''
# check the first line
# variable.search(regex,in_string)
if re.search("^# Exim filter", control_file[0]) is not None:
    if debug:
        print("valid file:", 0, control_file[0])

# now parse the file:
'''after we've finished this, we should have set:
    is_mail_redirect
    forward_email
    forward_line
    is_out_of_office
    vacation_section_start
    vacation_section_end
    alias_list
'''
for i in range(0, len(control_file), 1):
    # if debug:
        # print(i, control_file[i])
    this_line = control_file[i]

    ''' ==== Forward commands ============================================
        in this section we're interested in a line with a "deliver" command surrounded by blanks
    '''
    if re.search(r'\bdeliver\b', this_line):
        # is it commented?
        if not re.search('^#', this_line):
            is_mail_redirect = True
        else:
            is_mail_redirect = False

        # split the line up on spaces, return all
        forward_line_list = this_line.split()
        # the last one must be the address(es)
        forward_email = forward_line_list[len(forward_line_list) - 1]
        # we'll need this line for later
        forward_line = i
        if debug:
            print("redir:", i, is_mail_redirect, forward_email)

    ''' ==== Vacation section start ======================================
    starts with "if personal"
    '''
    if re.search("if personal", this_line):
        # is it commented?
        if not re.search('^#', this_line):
            is_out_of_office = True
        else:
            is_out_of_office = False

        vacation_section = True
        vacation_section_start = i
        vacation_line = i
        if debug:
            print("vacat:", i, is_out_of_office, this_line)

    # ==== vacation alias, there might be more than one
    #   alias myname@company.com
    if (vacation_section and re.search(r'\balias\b', this_line)):
        # get the email address part, split the line up on spaces, and get the last one
        line_list = this_line.split(" ")
        alias_list.append(line_list[-1])
        aliases_last_line = i
        # if this is empty or does not look like an email address, we'll deal with this at file write time
        if debug:
            print("alias:", i, alias_list)

    # ==== message file location
    #   file "$home/.vacation.msg"
    if (vacation_section and re.search(r'\bfile\b', this_line)): 
        line_list = this_line.split()
        vacation_file_linux_version = line_list[len(line_list) - 1]
        intVacationFileLine = i
        if debug:
            print("vfile:", i, vacation_file_linux_version)

    # ==== vacation from
    #   from "Firstname Secondname <recipient.name@company.co.uk>"
    if (vacation_section and re.search(r'\bfrom\b', this_line)): 
        first_quote     = this_line.find('"')
        first_angle     = this_line.find('<')
        second_angle    = this_line.find('>')
        
        # # only try to do the next bit if it's a properly formatted line
        if first_quote > 0 and first_angle > 0 and second_angle > 0:
            my_name       = this_line[first_quote + 1: first_angle - 1]
            email_address = this_line[first_angle + 1: second_angle]
            vacation_from_line = i
            if debug:
                print(" name:", i, my_name, "\nemail:", i, email_address)

    # ==== vacation section end
    if (vacation_section and re.search("endif", this_line)): 
        vacation_section_end = i
        vacation_section = False
        if debug:
            print('v end:', i, this_line)

    ''' ==== Vacation section end, , ends with endif ================================
    we're not interested in any of the rest of the file, it will (if defined) the user's own filter definitions
    we need to preserve them, but no more action is required
    ==== end of control file parsing ================================================
'''

''' now some sanity checking ====================================
'''

# if we have not yet retrieved valid user details, go get them
if valid_email(email_address) and len(my_name) > 5:
    if debug:
        print("\nvalid email:\n" " name:", i, my_name, "/ email:", email_address)
else:
    # get_user_details    
    my_name, email_address = get_user_details()
    if debug:
        print("\nvalid email:\n" " FAIL:", i, my_name, "/ email:", email_address)

# by now we have the linux version of where we think the vacation file should be, convert it to windows format
vacation_file_windows_version = vacation_file_linux_version.replace("$home", home_share)
vacation_file_windows_version = vacation_file_windows_version.replace("/","\\")
if debug:
    print("vfwin:", i, vacation_file_windows_version)

# read the vacation file into a list
if not control_file_read(vacation_file, vacation_file_path, debug):
    # failed to read the control file, try the template
    if not control_file_read(vacation_file, vacation_template, debug):
        # template failed as well, tell the user
        sg.popup('Required file(s) missing' + \
            '\n  failed to read control file:\t' + str(vacation_file_path) + \
            '\n  failed to read template file:\t' + str(vacation_template) +\
            '\nPlease report this error, program will now exit', title = "Error")
        exit()
if debug:
    print("vacation file =====================================================")
    for i in range(0, len(vacation_file), 1):
        print(str(i) + ":", vacation_file[i])
   
# which mode are we in?  and do some sanity checking
all_unset            = True
# if both is_mail_redirect and is_out_of_office are set, this is an error, so turn them off
if is_mail_redirect and is_out_of_office:
    is_mail_redirect = False
    is_out_of_office = False
    all_unset        = True

if is_mail_redirect or is_out_of_office:
    all_unset        = False

# we need a "\n" version of alias_list and vacation_file
my_aliases = "\n".join(alias_list)
my_message = "\n".join(vacation_file)

# OK, now we need to ask the user what to do
window_layout = [
    # [sg.Menu(menu_def, tearoff=True)],

    [sg.Text('You can choose to send a copy of every mail to someone else within your organisation or you can set an Out of Office message.')],
    [sg.Text('Please select one of the following options:')],

    [sg.Radio('send a copy of all my mail to:', "RADIO1", default=is_mail_redirect), sg.InputText(forward_email,  tooltip='who do you want to send the mails to?')],

    [sg.Radio('set Out of Office message:', "RADIO1", default=is_out_of_office)],
    [sg.InputText('My Name',  tooltip='My Name')],
    [sg.MLine(default_text=my_aliases, size=(80, 1), tooltip='a list of all the addresses people might send mail to you as'),],
    [sg.MLine(default_text=my_message, size=(80, 3), tooltip='your out of office message'),],
    [sg.Text('Each person will only receive the message once in a 10 day period, messages from mailing lists & spam will be ignored.')],

    [sg.Radio('turn off "Copy to" or "Out of Office" message', "RADIO1", default=all_unset)],

    # draw a line across the screen
    [sg.Text('_' * 100)],

    # and the action buttons at the bottom
    [sg.Submit(tooltip='Click to submit this form'), sg.Cancel()]]

window = sg.Window('email Assistant', window_layout, no_titlebar=False, default_element_size=(40, 1))

while True:

    # and then this is what we do if one of the buttons is clicked
    event, values = window.read()
    if event in (None, 'Cancel'):
        window.close()
        exit()

    # so if we got here - we need to check the inputs, and if all is well, write the files
    # 0: False, 1: 'recipient@company.co.uk', 2: False, 3: 'My Name', 4: 'my email address(es)\n', 5: 'I am currently out of the office.\nI will respond to your message on my return.\n', 6: True}
    is_mail_redirect = values[0]
    redirect_email   = values[1]
    is_ooo           = values[2]
    ooo_my_name      = values[3]
    ooo_my_aliases   = values[4]
    ooo_message      = values[5]
    is_cancel        = values[6]

    if debug:
        print("=========================================================================")
        print('   is_redirect: ',        is_mail_redirect)   
        print('redirect_email: ',          redirect_email)
        print('        is_ooo: ',                  is_ooo)       
        print('   ooo_my_name: ',             ooo_my_name)   
        print('ooo_my_aliases: ',          ooo_my_aliases)  
        print('   ooo_message: ',             ooo_message)   
        print('     is_cancel: ',               is_cancel)
         
    if is_mail_redirect:
        set_ok = set_redirect(True, redirect_email)

    if is_ooo:
        if debug:
            print(type(ooo_my_aliases))
        set_ok = set_vacation(True, ooo_my_name, ooo_my_aliases, ooo_message)   

    if is_cancel:
        set_ok = reset()

    if debug:
        print('        set_ok: ',               set_ok)
        print('  forward_line: ',               control_file[forward_line])
        print('  vacation_sec: ',               control_file[vacation_section_start])

    if set_ok:
        window.close()
        exit()
   
