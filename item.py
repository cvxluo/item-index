
class Item (object) :

    def __init__(self, name, imageURL, tags = []) :
        self.name = name
        self.imageURL = imageURL
        self.tags = tags

    def getSearchTerm (self) :
        return self.name.lower().replace("'", "")

    def addTag (self, tag) :
        self.tags.append(tag)
