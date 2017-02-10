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
footnotes_part, footnotes_el, footnotes_pq = load_part(source_doc.part.part_related_by(RT.FOOTNOTES))
def parse_elements(case, proof, source_path='', convert_to_xml=True, convert_to_html=True):
    document = Document(proof.docx)
    source_doc, source_pq = document, pq(document.element, parser='xml')
    footnotes_part, footnotes_el, footnotes_pq = load_part(source_doc.part.part_related_by(RT.FOOTNOTES))

    docname = source_path.rsplit('/', 1)[-1]
    data = dict()
    name_abbreviation, citation, data['year'] = get_docname_parts(docname)

    data['citation'] = Citation(citation)

    paragraphs = source_pq('w|p')
    footnotes_list = process_footnotes(footnotes_pq, source_pq)
    data['footnotes'] = Footnotes(footnotes_list)
    court = Court()

    # casename
    par_num = 0
    casename_string = get_new_casename_string(paragraphs[par_num])
    data['casename'] = Casename(casename_string, name_abbreviation)
    data['parties'] = Parties(casename_string)

    # date
    par_num = skip_blanks(paragraphs, par_num)
    date_string = process_xml(paragraphs[par_num])
    data['date'] = Date(date_string)
    court.set_lower_court(date_string)

    # judges
    par_num = skip_blanks(paragraphs, par_num)
    judges_string = process_xml(paragraphs[par_num])
    data['judges'] = Judges(judges_string)

    # categories
    par_num = skip_blanks(paragraphs, par_num)
    categories_string = process_xml(paragraphs[par_num])
    data['categories'] = Categories(categories_string)

    # headnotes
    par_num = skip_blanks(paragraphs, par_num)
    headnotes_list, par_num = get_paragraphs_with_style(paragraphs, 'Headnote')
    data['headnotes'] = Headnotes(headnotes_list)

    par_num = skip_blanks(paragraphs, par_num)
    history_list, par_num = get_paragraphs_with_style(paragraphs, 'History')
    history_list = get_casetext(0, history_list)
    data['history'] = CaseText(history_list)

    par_num = skip_blanks(paragraphs, par_num)
    appearance_list, par_num = get_paragraphs_with_style(paragraphs, 'Appearance')
    appearance_list = get_casetext(0, appearance_list)
    data['appearance'] = Appearance(appearance_list)

    par_num = skip_blanks(paragraphs, par_num)
    author_string = get_author(paragraphs[par_num])
    data['author'] = Author(author_string)

    par_num = skip_blanks(paragraphs, par_num)
    casetext_list = get_casetext(par_num, paragraphs)
    data['casetext'] = CaseText(casetext_list)

    return data
