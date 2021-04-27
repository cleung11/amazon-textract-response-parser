from trp.t_pipeline import add_page_orientation, order_blocks_by_geo
import trp.trp2 as t2
import trp as t1
import json
import os
import pytest
from trp import Document

current_folder = os.path.dirname(os.path.realpath(__file__))


def return_json_for_file(filename):
    with open(os.path.join(current_folder, filename)) as test_json:
        return json.load(test_json)


@pytest.fixture
def json_response():
    return return_json_for_file("test-response.json")


def test_serialization():
    """
    testing that None values are removed when serializing
    """
    bb_1 = t2.TBoundingBox(
        0.4, 0.3, 0.1, top=None)  # type:ignore forcing some None/null values
    bb_2 = t2.TBoundingBox(0.4, 0.3, 0.1, top=0.2)
    p1 = t2.TPoint(x=0.1, y=0.1)
    p2 = t2.TPoint(x=0.3, y=None)  # type:ignore
    geo = t2.TGeometry(bounding_box=bb_1, polygon=[p1, p2])
    geo_s = t2.TGeometrySchema()
    s: str = geo_s.dumps(geo)
    assert not "null" in s
    geo = t2.TGeometry(bounding_box=bb_2, polygon=[p1, p2])
    s: str = geo_s.dumps(geo)
    assert not "null" in s


def test_tblock():
    p = os.path.dirname(os.path.realpath(__file__))
    f = open(os.path.join(p, "data/gib.json"))
    j = json.load(f)
    t_document: t2.TDocument = t2.TDocumentSchema().load(j)
    new_order = order_blocks_by_geo(t_document)
    doc = t1.Document(t2.TDocumentSchema().dump(new_order))
    assert "Value 1.1.1" == doc.pages[0].tables[0].rows[0].cells[0].text.strip(
    )
    assert "Value 2.1.1" == doc.pages[0].tables[1].rows[0].cells[0].text.strip(
    )
    assert "Value 3.1.1" == doc.pages[0].tables[2].rows[0].cells[0].text.strip(
    )


def test_custom_tblock():
    p = os.path.dirname(os.path.realpath(__file__))
    f = open(os.path.join(p, "data/gib.json"))
    j = json.load(f)
    t_document: t2.TDocument = t2.TDocumentSchema().load(j)
    t_document.custom = {'testblock': {'here': 'is some fun stuff'}}
    assert 'testblock' in t2.TDocumentSchema().dumps(t_document)


def test_custom_page_orientation(json_response):
    doc = Document(json_response)
    assert 1 == len(doc.pages)
    lines = [line for line in doc.pages[0].lines]
    assert 22 == len(lines)
    words = [word for line in lines for word in line.words]
    assert 53 == len(words)
    t_document: t2.TDocument = t2.TDocumentSchema().load(json_response)
    t_document.custom = {'orientation': 180}
    new_t_doc_json = t2.TDocumentSchema().dump(t_document)
    assert "Custom" in new_t_doc_json
    assert "orientation" in new_t_doc_json["Custom"]
    assert new_t_doc_json["Custom"]["orientation"] == 180

    p = os.path.dirname(os.path.realpath(__file__))
    f = open(os.path.join(p, "data/gib.json"))
    j = json.load(f)
    t_document: t2.TDocument = t2.TDocumentSchema().load(j)
    t_document = add_page_orientation(t_document)
    assert -1 < t_document.pages[0].custom['Orientation'] < 2

    p = os.path.dirname(os.path.realpath(__file__))
    f = open(os.path.join(p, "data/gib_10_degrees.json"))
    j = json.load(f)
    t_document: t2.TDocument = t2.TDocumentSchema().load(j)
    t_document = add_page_orientation(t_document)
    assert 5 < t_document.pages[0].custom['Orientation'] < 15

    p = os.path.dirname(os.path.realpath(__file__))
    f = open(os.path.join(p, "data/gib__15_degrees.json"))
    j = json.load(f)
    t_document: t2.TDocument = t2.TDocumentSchema().load(j)
    t_document = add_page_orientation(t_document)
    assert 10 < t_document.pages[0].custom['Orientation'] < 20

    p = os.path.dirname(os.path.realpath(__file__))
    f = open(os.path.join(p, "data/gib__25_degrees.json"))
    j = json.load(f)
    t_document: t2.TDocument = t2.TDocumentSchema().load(j)
    t_document = add_page_orientation(t_document)
    assert 17 < t_document.pages[0].custom['Orientation'] < 30

    p = os.path.dirname(os.path.realpath(__file__))
    f = open(os.path.join(p, "data/gib__180_degrees.json"))
    j = json.load(f)
    t_document: t2.TDocument = t2.TDocumentSchema().load(j)
    t_document = add_page_orientation(t_document)
    assert 170 < t_document.pages[0].custom['Orientation'] < 190

    p = os.path.dirname(os.path.realpath(__file__))
    f = open(os.path.join(p, "data/gib__270_degrees.json"))
    j = json.load(f)
    t_document: t2.TDocument = t2.TDocumentSchema().load(j)
    t_document = add_page_orientation(t_document)
    assert -100 < t_document.pages[0].custom['Orientation'] < -80

    p = os.path.dirname(os.path.realpath(__file__))
    f = open(os.path.join(p, "data/gib__90_degrees.json"))
    j = json.load(f)
    t_document: t2.TDocument = t2.TDocumentSchema().load(j)
    t_document = add_page_orientation(t_document)
    assert 80 < t_document.pages[0].custom['Orientation'] < 100

    p = os.path.dirname(os.path.realpath(__file__))
    f = open(os.path.join(p, "data/gib__minus_10_degrees.json"))
    j = json.load(f)
    t_document: t2.TDocument = t2.TDocumentSchema().load(j)
    t_document = add_page_orientation(t_document)
    assert -10 < t_document.pages[0].custom['Orientation'] < 5

    doc = t1.Document(t2.TDocumentSchema().dump(t_document))
    for page in doc.pages:
        assert page.custom['Orientation']



def test_filter_blocks_by_type():
    block_list = [t2.TBlock(block_type=t2.TextractBlockTypes.WORD.name)]
    assert t2.TDocument.filter_blocks_by_type(block_list=block_list, textract_block_type=[t2.TextractBlockTypes.WORD]) == block_list
