# test scaffold

debug = True
# debug = False

from get_user_details import GetUserDetails


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

