import string
import re
from pyquery import PyQuery as pq
from scripts.entities import Footnote, FootnoteContent
from django.core.files.base import ContentFile


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

def remove_el(el):
    el.getparent().remove(el)

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

def clean_xml(xml):
    return re.sub(r"\s\&\s", " &amp; ", xml)

def get_casename_string(par):
    full_str = ""
    for run in pq(par)('w|r'):
        if run.style and run.style == 'FootnoteReference':
            footnote = Footnote(run.xml)
            full_str += footnote.format_for_xml()
        else:
            full_str += run.text
    return full_str

def get_casetext(par_num, paragraphs):
    casetext = []
    for par in paragraphs[par_num:]:
        full_str = ''
        for run in par:
            try:
                if run.style and run.style == 'FootnoteReference':
                    footnote = Footnote(run.xml)
                    full_str += footnote.format_for_xml()
            except:
                pass
            if run.text:
                full_str += re.sub(r'\t', '', run.text)
        casetext.append(full_str)
    return casetext

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
    author = ''
    for run in par:
        try:
            if 'Author' in run.xml:
                author += run.text
        except:
            pass
    return re.sub(r'\t', '', author)

def get_paragraphs_with_style(paragraphs, style):
    pars = []
    par_num = 0

    for idx, p in enumerate(paragraphs):
        if p.style == style:
            pars.append(p)
            par_num = idx
    return pars, par_num

def get_docname_parts(docname):
    citation = re.search(r'\d+\s+\w+.\s+\d+', docname).group()
    year = int(re.search(r'\(\d{4}\)\.proof\.docx$', docname).group()[1:].split(').proof.docx')[0])
    name_abbreviation = re.sub(',', '', docname.split(citation)[0].rstrip())
    return name_abbreviation, citation, year


def write_file(filename, case, data, filetype='xml'):
    content = ""
    if filetype == 'xml':
        content = xml_template.substitute(
            casename=data['casename'].xml,
            citation=data['citation'].xml,
            decisiondate=data['date'].xml[0],
            parties=data['parties'].xml,
            decisiondate_two=data['date'].xml[1],
            decisiondate_other=data['date'].xml[2],
            attorneys=data['appearance'].xml,
            judges=data['judges'].xml,
            author=data['author'].xml,
            casetext=data['casetext'].xml,
            categories=data['categories'].html,
            headnotes=data['headnotes'].html,
            footnotes=data['footnotes'],
            )
    elif filetype == 'html':
        content = html_template.substitute(
            casename=data['casename'].html,
            decisiondate=data['date'].html,
            attorneys=data['appearance'].html,
            judges=data['judges'].html,
            author=data['author'].html,
            casetext=data['casetext'].html,
            categories=data['categories'].html,
            headnotes=data['headnotes'].html,
            )

    return ContentFile(content)


xml_template = string.Template("""<?xml version='1.0' encoding='utf-8'?>
<mets xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.loc.gov/METS/">
  <dmdSec ID="case">
    <mdWrap MDTYPE="OTHER" OTHERMDTYPE="HLS-CASELAW-CASEXML">
      <xmlData>
        <case xmlns="http://nrs.harvard.edu/urn-3:HLS.Libr.US_Case_Law.Schema.Case:v1" case_id="{case.id}">
            $casename
            $citation
            $decisiondate
        </case>
      </xmlData>
    </mdWrap>
  </dmdSec>
    <fileSec>
      <fileGrp USE="casebody">
        <file ID="casebody_id" MIMETYPE="text/xml">
          <FContent>
            <xmlData>
              <casebody xmlns="http://nrs.harvard.edu/urn-3:HLS.Libr.US_Case_Law.Schema.Case_Body:v1" firstpage="{case.first_page}" lastpage="{case.last_page}">
                $parties
                $decisiondate_two
                $decisiondate_other
                $judges
                $categories
                $headnotes
                $attorneys
                $casetext
                $footnotes
              </casebody>
            </xmlData>
          </FContent>
        </file>
      </fileGrp>
    </fileSec>
</mets>
""")

html_template = string.Template("""$casename
$decisiondate
$attorneys
$judges
$categories
$headnotes
$casetext
""")
