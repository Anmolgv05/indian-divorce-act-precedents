import os
import pytest
from src.scrape import parse_judgment_html, extract_doc_id, parse_date_from_title

SAMPLE_HTML = """
<!DOCTYPE HTML>
<html>
<head><title>Sample Case vs Another Case on 15 March, 2012</title></head>
<body>
    <h2 class="doc_title">Sample Case vs Another Case on 15 March, 2012</h2>
    <h3 class="docsource_main">Delhi High Court</h3>
    <div class="doc_citations">Equivalent citations: 2012 (1) DMC 123</div>
    <div class="judgments">
        <p id="p_1">1. This is a petition under Section 10 of the Indian Divorce Act, 1869 seeking dissolution of marriage on the ground of cruelty and desertion.</p>
        <p id="p_2">2. The marriage was solemnized between the parties according to Christian rites.</p>
        <p id="p_3">3. The appellant contended that the respondent treated him with extreme cruelty.</p>
        <p id="p_4">4. In the result, the appeal is allowed and decree of divorce is granted.</p>
    </div>
</body>
</html>
"""

def test_extract_doc_id():
    assert extract_doc_id("https://indiankanoon.org/doc/1401518/") == "1401518"
    assert extract_doc_id("https://indiankanoon.org/docfragment/476455/?formInput=foo") == "476455"
    with pytest.raises(ValueError):
        extract_doc_id("https://indiankanoon.org/search/?formInput=foo")

def test_parse_date_from_title():
    date_str, year = parse_date_from_title("Sample Case vs Another Case on 15 March, 2012")
    assert date_str == "2012-03-15"
    assert year == 2012

    date_str2, year2 = parse_date_from_title("Ancient Case vs Other in 1985")
    assert date_str2 == "1985-01-01"
    assert year2 == 1985

def test_parse_judgment_html():
    parsed = parse_judgment_html(SAMPLE_HTML, doc_id="999999", url="https://indiankanoon.org/doc/999999/")
    assert parsed["doc_id"] == "999999"
    assert parsed["court"] == "Delhi High Court"
    assert parsed["date"] == "2012-03-15"
    assert parsed["year"] == 2012
    assert parsed["citations"] == "Equivalent citations: 2012 (1) DMC 123"
    assert len(parsed["paragraphs"]) == 4
    assert parsed["paragraphs"][0]["p_id"] == "p_1"
    assert "cruelty and desertion" in parsed["paragraphs"][0]["text"]
    assert "divorce is granted" in parsed["paragraphs"][3]["text"]


def test_anchor_tag_spacing():
    html = """
    <html><body>
    <div class="judgments">
        <p id="p_1">Petition filed under<a href="/doc/1387951/">Section 10</a>of the Divorce Act.</p>
    </div>
    </body></html>
    """
    parsed = parse_judgment_html(html, doc_id="111", url="https://indiankanoon.org/doc/111/")
    assert parsed["paragraphs"][0]["text"] == "Petition filed under Section 10 of the Divorce Act."

