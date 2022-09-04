import instaloader

USER = input("Enter Account Username : ")
PASSWORD = input("Enter Account Passsword : ")
L = instaloader.Instaloader()
L.login("{}".format(USER), "{}".format(PASSWORD))   
L.save_session_to_file(filename = '{}.session'.format(USER))