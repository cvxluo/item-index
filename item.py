
class Item (object) :

    def __init__(self, name, imageURL) :
        self.name = name
        self.imageURL = imageURL
        """
        if tags != None :
            self.tags = tags
        """

    def getSearchTerm (self) :
        return self.name.lower().replace("'", "")
