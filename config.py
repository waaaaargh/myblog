import ConfigParser

class Configuration:
    def __init__(self):
        pass

    def load_from_file(self,filename):
        parser = ConfigParser.RawConfigParser()
        parser.read(filename)

        self.instance_name = parser.get("base", "blog_name")
        self.instance_owner = parser.get("base", "blog_owner")
        self.base_path = parser.get("base", "base_path")

        self.username = parser.get("admin", "username")
        self.password = parser.get("admin", "password")
 
        self.database_uri = parser.get("db", "database_uri")
