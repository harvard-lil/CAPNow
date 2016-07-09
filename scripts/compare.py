import difflib
import sys
from lxml import etree
from docx.oxml import parse_xml

from convert import load_doc

from_path, to_path = sys.argv[1:]

from_doc, from_pq = load_doc(from_path)
to_doc, to_pq = load_doc(to_path)

def print_diff(from_part, to_part):
    print("-------\nDIFFING %s\n-------" % from_part.partname)
    from_xml = etree.tostring(parse_xml(from_part.blob), pretty_print=True, encoding=str)
    to_xml = etree.tostring(parse_xml(to_part.blob), pretty_print=True, encoding=str)

    open('a', 'w').write(from_xml)
    open('b','w').write(to_xml)

    diff = difflib.unified_diff(from_xml.split("\n"), to_xml.split("\n"))
    print("\n".join(diff))

print_diff(from_doc.part, to_doc.part)

for key, val in from_doc.part.related_parts.items():
    print_diff(val, to_doc.part.related_parts[key])