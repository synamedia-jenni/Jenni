from html import escape
from typing import List
from textwrap import dedent


def bool2groovy(b: bool) -> str:
    return "true" if b else "false"


def groovy_string_list(l: List[str]) -> str:
    if l:
        return ", ".join([quote1or3xs(s) for s in l])
    else:
        return ""


def tidy_text(s: str) -> str:
    """Strips and un-indents the text"""
    s = s.lstrip("\n")
    s = s.rstrip()
    return dedent(s)


def quote3xs(s: str) -> str:
    """
    Groovy formatted triple quoted string
    :param s: string to return as triple-single-quoted, IE like '''<s>'''
    :return: triple-single-quoted string
    """
    if "\\" in s:
        s = s.replace("\\", "\\\\")
    if "'''" in s:
        s = s.replace("'''", "\\'''")
    return f"'''{s}'''"


def quote1s(s: str) -> str:
    """
    Groovy formatted single quoted string
    :param s: string to return as single-quoted, IE like '<s>'
    :return: single-quoted string
    """
    if "\\" in s:
        s = s.replace("\\", "\\\\")
    if "'" in s:
        s = s.replace("'", "\\'")
    return f"'{s}'"


def quote1or3xs(s: str) -> str:
    """
    Groovy formatted string (single or triple quoted as necessary)
    :param s: string
    :return: single or triple quoted string
    """
    if "\n" in s:
        return quote3xs(s)
    if "\\" in s:
        s = s.replace("\\", "\\\\")
    if "'" in s:
        s = s.replace("'", "\\'")
    return f"'{s}'"


def quote_list(list_of_str: List[str]) -> str:
    """
    Groovy formatted list of strings
    :param list_of_str: list of strings
    :return:
    """
    return "[" + (", ".join([quote1or3xs(s) for s in list_of_str])) + "]"


def html_link(url: str, text: str = "") -> str:
    if text:
        body = text
    else:
        body = escape(url)
    return f'<a href="{url}">{body}</a>'
