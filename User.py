class User:
    def __init__(self, name, password):
        self.name = name
        self.password = password
    
    def match_password(self, password):
        if password == self.password:
            return self.name
        return None
    
