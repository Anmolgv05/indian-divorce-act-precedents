import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from parse_clean import is_substantive_sec10_case, clean_whitespace


def test_clean_whitespace():
    raw = "This   is  a \t line   with   extra    spaces.  "
    assert clean_whitespace(raw) == "This is a line with extra spaces."


def test_filter_law_commission_report():
    case = {
        "doc_id": "86162589",
        "title": "The Indian Divorce Act 1869",
        "court": "Law Commission Report",
        "full_text": "Report on Section 10 of the Indian Divorce Act 1869",
        "paragraphs": [{"p_id": "p_1", "text": "1"}, {"p_id": "p_2", "text": "2"}, {"p_id": "p_3", "text": "3"}]
    }
    is_sub, reason = is_substantive_sec10_case(case)
    assert not is_sub
    assert "Law Commission" in reason


def test_filter_non_divorce_act_case():
    case = {
        "doc_id": "12345",
        "title": "Landlord vs Tenant on 10 May, 2015",
        "court": "Delhi High Court",
        "full_text": "This is a suit for eviction under Section 10 of the Delhi Rent Control Act.",
        "paragraphs": [{"p_id": "p_1", "text": "1"}, {"p_id": "p_2", "text": "2"}, {"p_id": "p_3", "text": "3"}]
    }
    is_sub, reason = is_substantive_sec10_case(case)
    assert not is_sub
    assert "Indian Divorce Act" in reason


def test_filter_short_order():
    case = {
        "doc_id": "54321",
        "title": "A vs B on 1 Jan, 2020",
        "court": "Bombay High Court",
        "full_text": "Section 10 of the Divorce Act. Adjourned.",
        "paragraphs": [{"p_id": "p_1", "text": "Adjourned."}]
    }
    is_sub, reason = is_substantive_sec10_case(case)
    assert not is_sub
    assert "Insufficient length" in reason


def test_retain_substantive_case():
    case = {
        "doc_id": "600946",
        "title": "Kuruvilla Varghese vs Sapnam Elizabeth Joseph on 25 May, 2007",
        "court": "Kerala High Court",
        "full_text": "Petition under Section 10 of the Indian Divorce Act, 1869 for dissolution of marriage.",
        "paragraphs": [{"p_id": "p_1", "text": "1"}, {"p_id": "p_2", "text": "2"}, {"p_id": "p_3", "text": "3"}]
    }
    is_sub, reason = is_substantive_sec10_case(case)
    assert is_sub
