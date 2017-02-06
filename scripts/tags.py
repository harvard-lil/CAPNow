class TagLibrary(dict):
    def format_tag(self, tname):
        return lambda x: "<"+tname+">"+x+"</"+tname+">"
    pass

tag = TagLibrary()
tag.h1 = tag.format_tag("h1")
tag.h2 = tag.format_tag("h2")
tag.h3 = tag.format_tag("h3")
tag.h4 = tag.format_tag("h4")
tag.em = tag.format_tag("em")
tag.party = tag.format_tag("party")
tag.parties = tag.format_tag("parties")
tag.name = tag.format_tag("name")
tag.sup = tag.format_tag("sup")
tag.decisiondate = tag.format_tag("decisiondate")
tag.otherdate = tag.format_tag("otherdate")
tag.judges = tag.format_tag("judges")
