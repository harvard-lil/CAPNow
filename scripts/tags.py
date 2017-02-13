class TagLibrary(dict):
    def format_tag(self, tname):
        return lambda x: "<"+tname+">"+x+"</"+tname+">"
    pass

tag = TagLibrary()
# html tags
tag.h1 = tag.format_tag("h1")
tag.h2 = tag.format_tag("h2")
tag.h3 = tag.format_tag("h3")
tag.h4 = tag.format_tag("h4")
tag.em = tag.format_tag("em")
tag.p = tag.format_tag("p")
tag.bold = tag.format_tag("bold")
tag.sup = tag.format_tag("sup")
# xml tags
tag.party = tag.format_tag("party")
tag.parties = tag.format_tag("parties")
tag.name = tag.format_tag("name")
tag.decisiondate = tag.format_tag("decisiondate")
tag.otherdate = tag.format_tag("otherdate")
tag.judges = tag.format_tag("judges")
tag.categories = tag.format_tag("categories")
tag.author = tag.format_tag("author")
tag.attorneys = tag.format_tag("attorneys")
tag.court = tag.format_tag("court")
tag.citation = tag.format_tag("citation")
