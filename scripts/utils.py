import re
from pyquery import PyQuery as pq
from scripts.entities import Footnote, FootnoteContent
from scripts.tags import *
def process_xml(par):
    text = ''
    for run in pq(par)('w|r'):
        text += run.text
    return text

def skip_blanks(paragraphs, par_num):
    par_num += 1
    while not has_text(paragraphs[par_num]):
        par_num += 1
    return par_num

def strip_xml(xml_str):
    rx = re.compile('<\s*\w.*?>|</\s*\w.*?>|\n|\t|\r|\s{2}')
    return rx.sub('',xml_str)

def process_footnotes(footnotes_pq, source_pq):
    footnotes = footnotes_pq('w|footnote').children()
    # remove blanks
    for query in (source_pq, footnotes_pq('w|footnote:not([w|type])')):
        for p in query('w|p'):
            if not has_text(p):
                remove_el(p)

    footnote_list = []
    count = 1
    for footnote in footnotes:
        """
        if FootnoteReference style exists in footnote then this is a new footnote
        otherwise it's a continuation of the last footnote
        """
        raw_str = strip_xml(footnote.xml)
        if len(raw_str):
            if "FootnoteReference" in footnote.xml:
                footnote = FootnoteContent(raw_str, count)
                footnote_list.append(footnote)
                count += 1
            elif len(footnote_list):
                footnote = footnote_list.pop()
                footnote.add_to_xml(raw_str)
                footnote_list.append(footnote)
            else:
                pass

    return footnote_list

def has_text(el):
    return not re.match(r'^\s*$', pq(el).text())
def get_new_casename_string(par):
    full_str = ""
    for run in pq(par)('w|r'):
        if run.style and run.style == 'FootnoteReference':
            footnote = Footnote(run.xml)
            full_str += footnote.format_for_xml()
        elif 'smallCaps' in run.xml:
            full_str += run.text.upper()
        else:
            full_str += run.text
    return full_str

def get_author(par):
    for run in par:
        if 'Author' in run.xml:
            return run.text
