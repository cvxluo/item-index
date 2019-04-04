
class Item (object) :

    def __init__(self, name, imageURL, tags = None) :
        self.name = name
        self.imageURL = imageURL
        if tags == None :
            self.tags = {}
        else :
            self.tags = tags

    def getSearchTerm (self) :
        return self.name.lower().replace("'", "")

    def addTag (self, tagType, tag) :
        if tagType in self.tags :
            self.tags[tagType].append(tag)

        else :
            self.tags[tagType] = [tag]

    def deleteTag(self, tagType, tag) :
        self.tags[tagType].remove(tag)




    def __lt__ (self, other) :
        return self.name < other.name


    def __str__ (self) :
        return self.name + " " + self.imageURL
