from scripts.convert import *
from scripts.tags import tag
from firmament.models import Case
from datetime import datetime
source_path = "/Users/aaizman/Documents/firmament/docs/originals/Bayless v. TTS Trio Corporation, 474 Mass. 1 (2016).docx"
document = Document(source_path)
source_doc, source_pq = document, pq(document.element, parser='xml')
template_path = 'sources/Case Template.docx'

def has_text(el):
    return not re.match(r'^\s*$', pq(el).text())

def skip_blanks(paragraphs, par_num):
    par_num += 1
    while not has_text(paragraphs[par_num]):
        par_num += 1
    return par_num

def get_elements:
    pq(source_pq('w|p')[:4]).remove()
    paragraphs = source_pq('w|p')
    bookmarks = get_bookmarks(source_pq("w|highlight[w|val='yellow']"))

    # casename
    par_num = 0
    casename_string = get_casename_string(paragraphs[par_num])

    # date
    par_num = skip_blanks(paragraphs, par_num)
    date_stripped = strip_xml(paragraphs[par_num].xml)
    decision_date = get_latest_date(date_stripped)

    # judges
    par_num = skip_blanks(paragraphs, par_num)
    judges = process_xml(paragraphs[par_num].xml)

    # categories
    par_num = skip_blanks(paragraphs, par_num)
    categories = process_xml(paragraphs[par_num])

    # headnotes
    headnotes, par_num = get_headnotes(par_num)



def get_latest_date(date_str):
    return datetime.strptime(date_str.split(' - ')[1], '%B %d, %Y.')

def strip_xml(xml_str):
    # includes anything inside of script tags as if it's in dom
    # maybe that should be changed
    rx = re.compile('<\s*\w.*?>|</\s*\w.*?>|\n|\t|\r|\s{2}')
    return rx.sub('',xml_str)

def process_xml(par):
    text = ''
    for run in pq(par)('w|r'):
        text += run.text
    return text

def get_casename_string(par):
    full_str = ""
    for run in pq(par)('w|r'):
        if run.style and run.style == 'FootnoteReference':
            footnote = Footnote(run.xml)
            full_str += footnote.format_xml()
        else:
            full_str += run.text
    return full_str


class Parties:
    def format_for_xml(self, raw_str):
        raw_str = re.sub(r"([A-Z][A-Z\s+.]+)", lambda entity: tag.party(entity.group().title()), raw_str)
        return tag.parties(raw_str)

    def format_for_html(self, raw_str):
        raw_str = re.sub(r"([A-Z][A-Z\s+.]+)", lambda entity: tag.em(entity.group().title()), raw_str)
        return tag.h1(raw_str)

    def __init__(self, raw_str):
        self.xml = self.format_for_xml(raw_str)
        self.html = self.format_for_html(raw_str)

class Casename:
    def get_footnote_num(self, footnote_str):
        return re.search(r"\d+", footnote_str).group()

    def format_for_db(self, raw_str):
        name = re.sub(r"<footnotemark>\d+<\/footnotemark>", "", raw_str)
        return re.sub(r"[A-Z][A-Z]+", lambda entity: entity.group().title(), name)

    def format_for_xml(self, raw_str):
        name = re.sub(r"<footnotemark>\d+<\/footnotemark>", "", raw_str)
        title = re.sub(r"[A-Z][A-Z]+", lambda entity: entity.group().title(), name)
        return tag.name(title)

    def format_for_html(self, raw_str):
        name = re.sub(r"<footnotemark>\d+<\/footnotemark>", lambda footnote: tag.sup(self.get_footnote_num(footnote.group())), raw_str)
        title = re.sub(r"[A-Z][A-Z\s+.]+", lambda entity: tag.em(entity.group().title()), name)
        return tag.h1(title)

    def __init__(self, raw_str):
        self.xml = self.format_for_xml(raw_str)
        self.db_str = self.format_for_db(raw_str)
        self.html = self.format_for_html(raw_str)

class Footnote:
    number = None
    content = ""

    def format_xml(self):
        return "<footnotemark>%s</footnotemark>" % self.number

    def __init__(self, xml):
        footnote_id = re.search(r'footnoteReference\s+w\:id\=\"(\d+)\"', xml)
        self.number=int(footnote_id.groups()[0])

def get_bookmarks(bookmark_pq):
    bookmarks = []
    for i, highlight_run in enumerate(bookmark_pq):
        highlight_run = pq(highlight_run).closest('w|r')
        bookmark_name = "Headnote%s%s" % ("End" if i % 2 else "Start", int(i/2))
        highlight_run.after(pq([
            make_el(highlight_run[0], "w:bookmarkStart", {"w:id": str(i), "w:name": bookmark_name}),
            make_el(highlight_run[0], "w:bookmarkEnd", {"w:id": str(i)})]))
        remove_el(highlight_run[0])
        bookmarks.append(bookmark_name)
    return bookmarks

# headnotes: json.dumped list of paragraphs
def get_headnotes(par_num):
    headnotes = []
    while has_text(paragraphs[par_num]):
        processed_headnote = process_xml(paragraphs[par_num])
        headnotes.append(processed_headnote)
        # do_headnote_stuff(paragraphs[par_num])
        par_num += 2
    return headnotes, par_num


    #
    # while has_text(paragraphs[par_num]):
    #     # processed_headnote = process_xml(paragraphs[par_num])
    #     # headnotes.append(processed_headnote)
    #     par_num += 2

def do_headnote_stuff(headnote):
    # TODO: figure out what the hell deepcopy does, why is it necessary?
    for run in pq(headnote).closest('w|p')('w|r'):
        import ipdb; ipdb.set_trace()
        run = pq(run)
        parts = re.split(r'\[.*?\]', run('w|t').text())
        if len(parts) > 1:
            new_els = []
            for i, part in enumerate(parts):
                if i!= 0:
                    new_els.extend(parse_xml_fragment(run[0], reference_template.format(bookmark_start=bookmarks.pop(0), bookmark_end=bookmarks.pop(0))))
                new_run = deepcopy(run[0])
                pq(new_run)('w|t').text(
                    ("]" if i != 0 else "") + part + ("[" if i != len(parts) - 1 else "")
                )
                new_els.append(new_run)
            run.after(pq(new_els))
            remove_el(run[0])
        # print(new_els)

# headnotes =
while has_text(paragraphs[par_num]):
    # print()
    import ipdb; ipdb.set_trace()
    paragraphs[par_num].style = 'Headnote'
    par_num += 2


#
# def get_casename(par):
#     parties = []
#     party = Party()
#     for run in pq(par)('w|r'):
#         if run.style and run.style == 'FootnoteReference':
#             footnote_id = re.search(r'footnoteReference\s+w\:id\=\"(\d+)\"', run.xml)
#             party.footnote = int(footnote_id.groups()[0])
#         elif run.text == 'vs' or run.text == 'v':
#             parties.append(party)
#             party = Party()
#         else:
#             name = re.search(r'\w{1,}\s?', run.text)
#             if name:
#                 party.name += run.text
#     parties.append(party)
#     for p in parties:
#          nada, p.name, p.details = re.split(r'([A-Z](?:[A-Z.\-_]\s?)+)', p.name)
#     return parties
