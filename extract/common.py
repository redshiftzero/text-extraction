import re

from .utils import (
    pdfdata_to_text,
    text_after_line_numbers,
    text_from_element_lxml,
    text_from_element_siblings_lxml,
)


def extract_simple_pdf(data, metadata):
    return pdfdata_to_text(data)


def extract_line_numbered_pdf(data, metadata):
    return text_after_line_numbers(pdfdata_to_text(data))


def extract_sometimes_numbered_pdf(data, metadata):
    """
    A few states have bills both with numbered lines and without.
    In these cases, we need to look at the start of the lines
    to determine which extraction function to use.
    """

    pdf_text = pdfdata_to_text(data)
    lines = pdf_text.split("\n")

    # Looking for lines that begin with a number
    pattern = re.compile(r"^\s*\d+\s+(.*)", flags=re.MULTILINE)
    number_of_numbered_lines = pattern.findall(pdf_text)

    # If more than 10% of the text begins with numbers, then we are
    # probably looking at a bill with numbered lines.
    THRESHOLD_NUMBERED_PDF = 0.10

    ratio_of_numbered_lines = len(number_of_numbered_lines) / len(lines)

    if ratio_of_numbered_lines > THRESHOLD_NUMBERED_PDF:
        return extract_line_numbered_pdf(data, metadata)
    else:
        return extract_simple_pdf(data, metadata)


def extract_pre_tag_html(data, metadata):
    """
    Many states that provide bill text on HTML webpages (e.g. AK, FL)
    have the text inside <pre> tags (for preformatted text).
    """

    text_inside_matching_tag = text_from_element_lxml(data, ".//pre")
    return text_after_line_numbers(text_inside_matching_tag)


def extract_from_p_tags_html(data, metadata):
    """
    For a few states providing bill text in HTML, we just want to get all
    the text in paragraph tags on the page. There may be several paragraphs.
    """

    text = text_from_element_siblings_lxml(data, ".//p")
    return text


def extract_from_code_tags_html(data, metadata):
    """
    Some states (e.g. IL) have the bill text inside
    <code> tags (as it renders as fixed-width).
    """

    text = text_from_element_siblings_lxml(data, ".//code")
    return text
