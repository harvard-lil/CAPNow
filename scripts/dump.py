import sys
from lxml import etree
from docx.oxml import parse_xml

from convert import load_doc

target_path = sys.argv[1]

target_doc, _ = load_doc(target_path)

def print_xml(part):
    print("-------\nPART %s\n-------" % part.partname)
    print(etree.tostring(parse_xml(part.blob), pretty_print=True, encoding=str))

print_xml(target_doc.part)

for key, val in target_doc.part.related_parts.items():
    print_xml(val)