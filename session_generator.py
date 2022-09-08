import sys
import subprocess
import pkg_resources

required = {'instaloader'}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing = required - installed

if missing:
    print("Instaloader Module was missing. So Installing...")
    python = sys.executable
    subprocess.check_call([python, '-m', 'pip', 'install', *missing], stdout=subprocess.DEVNULL)

import instaloader


USER = input("Enter Account Username : ").lower()
PASSWORD = input("Enter Account Passsword : ")
L = instaloader.Instaloader()
try:
    try:
        L.login("{}".format(USER), "{}".format(PASSWORD))
    except instaloader.exceptions.TwoFactorAuthRequiredException:
        two_factor_code = int(input("Enter your two factor OTP : "))
        try:
            L.two_factor_login(two_factor_code)
        except instaloader.exceptions.BadCredentialsException:
            print("2FA verification code is invalid.")
    L.save_session_to_file(filename = '{}.session'.format(USER))
except instaloader.exceptions.BadCredentialsException:
    print("Wrong Password.")
except instaloader.exceptions.InvalidArgumentException:
    print("Wrong Username.")
except instaloader.exceptions.ConnectionException:
    print("Connection to Instagram failed.")
except BaseException:
    print("Unknown Error Occurred.")
