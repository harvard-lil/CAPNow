import re

from scripts.convert import *
from scripts.tags import tag
from scripts.utils import *
from scripts.entities import *
from firmament.models import Case
from datetime import datetime

source_path = "/Users/aaizman/Documents/firmament/docs/originals/Bayless v. TTS Trio Corporation, 474 Mass. 1 (2016).docx"
document = Document(source_path)
source_doc, source_pq = document, pq(document.element, parser='xml')
template_path = 'sources/Case Template.docx'

def get_elements():
    pq(source_pq('w|p')[:4]).remove()
    paragraphs = source_pq('w|p')
    bookmarks = get_bookmarks(source_pq("w|highlight[w|val='yellow']"))

    # casename
    par_num = 0
    casename_string = get_casename_string(paragraphs[par_num])
    casename = Casename(casename_string)
    parties = Parties(casename_string)

    # date
    par_num = skip_blanks(paragraphs, par_num)
    date_string = process_xml(paragraphs[par_num])
    date = Date(date_string)

    # judges
    par_num = skip_blanks(paragraphs, par_num)
    judges_string = process_xml(paragraphs[par_num])
    judges = Judges(judges_string)

    # categories
    par_num = skip_blanks(paragraphs, par_num)
    categories_string = process_xml(paragraphs[par_num])
    categories = Categories(categories_string)

    # headnotes
    par_num = skip_blanks(paragraphs, par_num)
    headnotes, par_num = get_headnotes(par_num)

def get_casename_string(par):
    full_str = ""
    for run in pq(par)('w|r'):
        if run.style and run.style == 'FootnoteReference':
            footnote = Footnote(run.xml)
            full_str += footnote.format_for_xml()
        else:
            full_str += run.text
    return full_str

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
        # processed_headnote = process_xml(paragraphs[par_num])
        # headnotes.append(processed_headnote)
        headnotes.append(paragraphs[par_num])
        # do_headnote_stuff(paragraphs[par_num])
        par_num += 2
    return headnotes, par_num

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
