import instaloader

USER = input("Enter Account Username : ")
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
