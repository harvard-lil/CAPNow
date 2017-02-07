import re
from pyquery import PyQuery as pq

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

def has_text(el):
    return not re.match(r'^\s*$', pq(el).text())
