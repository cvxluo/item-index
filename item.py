
class Item (object) :

    def __init__(self, name, imageURL = None, tags = None) :
        if (name) :
            self.name = name

        if (imageURL) :
            self.imageURL = imageURL

        if tags == None :
            self.tags = {}
        else :
            self.tags = tags



    def fromStore (line) :
        data = line.split()
        name = " ".join(data[0].split("$"))

        storedTags = {}
        if (len(data) > 2) :
            tagData = data[2].split("&")
            for tag in tagData :
                nameSplit = tag.split(":")
                tagName = nameSplit[0].replace('$', ' ')

                t = nameSplit[1].split(',')

                storedTags[tagName] = []
                for attribute in t :
                    storedTags[tagName].append(attribute.replace('$', ' '))


        item = Item(name, data[1], storedTags)
        return item



    def getSearchTerm (self) :
        return self.name.lower().replace("'", "")

    def addTag (self, tagType, tag) :
        if tagType in self.tags :
            self.tags[tagType].append(tag)

        else :
            self.tags[tagType] = [tag]

    def deleteTag(self, tagType, tag) :
        self.tags[tagType].remove(tag)


    def storeFormat(self) :
        item = []
        if (self.name) :
            item.append("$".join(self.name.split()))

        if (self.imageURL) :
            item.append(self.imageURL)


        t = []

        if (self.tags) :
            for tagType, aTags in self.tags.items() :
                newTag = ""
                newTag += tagType.replace(' ', '$') + ":"

                storeTags = []
                for tag in aTags :
                    storeTags.append(tag.replace(' ', '$'))

                newTag += ','.join(storeTags)

                t.append(newTag)

        item.append('&'.join(t))

        data = ' '.join(item)
        return data




    def __lt__ (self, other) :
        return self.name < other.name


    def __str__ (self) :
        return self.name + " " + self.imageURL
