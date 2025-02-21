from Keypad import Keypad
from User import User


class SecurityMeansController:

    def __init__(self, row_pins, col_pins):
        self.user_loged = None
        self.password = ''
        self.password_encode = ''
        self.users = []
        self.keypad = Keypad(row_pins=row_pins, col_pins=col_pins)
    
    def create_user_with_password(self, password, name):
        self.users.append(User(name, password))
    
    def check_access_key_pad(self):
        for user in self.users:
            name = user.match_password(self.password)
            if name:
                self.user_loged = name
                break
    
    def user_authenticated(self):
        if self.user_loged:
            return self.user_loged
            self.user_loged = None
        else:
            return False
    
    def clear(self):
        self.user_loged = None
        self.password = ''
        self.password_encode = ''
    
    def scan_key_pad(self):
        key = self.keypad.scanKey()
        if key:
            if key == "#":
                self.check_access_key_pad()
                self.password = ''
                self.password_encode = ''
            else:
                self.password += key
                self.password_encode += "*"
