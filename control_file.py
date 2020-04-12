# file read/write functions for emailAssistant.py
import PySimpleGUI as sg

# read the control file into a list, strip off trailing whitespace or newlines
def control_file_read(control_file, control_file_path, debug = False):
    if debug:
        print("attempting to open:", control_file_path)
    try: 
        with open(control_file_path, 'r') as f:
            # note that here we're using += which appends to an already existing list instead of creating a new local one
            control_file += [line.rstrip() for line in f]
    except Exception as error:
        # we couldn't open the file for some reason
        if debug:
            print(error)
        return False
    # otherwise, it worked
    return True

# write the control file to file, put back newlines
def control_file_write(control_file, control_file_path, debug = False):
    if debug:
        print("writing to file:", control_file_path)
    try: 
        with open(control_file_path, 'w') as f:
            for line_contents in control_file:
                f.write("%s\n" % line_contents)
    except Exception as error:
        # we couldn't write to the file
        sg.popup(error, 'please report this', title = 'error')
        return False
    # otherwise, it worked
    return True

