"""
Various helper functions that padsprod uses. Mostly for interacting with
users in a nice way.
"""

import argparse
import binascii
import math
import string
import sys
from pathlib import Path as path

import colorama
import questionary

SUBSPY_ROOT = path(__file__).resolve().parent

def set_terminal_title(title):
    if sys.stdout.isatty():
        sys.stdout.write(colorama.ansi.set_title(title))
        sys.stdout.flush()

SUPPORTED_LANGUAGES = [
    {"code": "BG", "language": "Bulgarian"},
    {"code": "ZH", "language": "Chinese"},
    {"code": "CS", "language": "Czech"},
    {"code": "DA", "language": "Danish"},
    {"code": "NL", "language": "Dutch"},
    {"code": "EN", "language": "English"},
    {"code": "ET", "language": "Estonian"},
    {"code": "FI", "language": "Finnish"},
    {"code": "FR", "language": "French"},
    {"code": "DE", "language": "German"},
    {"code": "EL", "language": "Greek"},
    {"code": "HU", "language": "Hungarian"},
    {"code": "IT", "language": "Italian"},
    {"code": "JA", "language": "Japanese"},
    {"code": "LV", "language": "Latvian"},
    {"code": "LT", "language": "Lithuanian"},
    {"code": "PL", "language": "Polish"},
    {"code": "PT", "language": "Portuguese"},
    {"code": "RO", "language": "Romanian"},
    {"code": "RU", "language": "Russian"},
    {"code": "SK", "language": "Slovak"},
    {"code": "SL", "language": "Slovenian"},
    {"code": "ES", "language": "Spanish"},
    {"code": "SV", "language": "Swedish"},
    # abbr
    {"code": "BG", "language": "bul"},
    {"code": "ZH", "language": "chs"},
    {"code": "CS", "language": "cze"},
    {"code": "DA", "language": "dan"},
    {"code": "NL", "language": "dut"},
    {"code": "EN", "language": "eng"},
    {"code": "ET", "language": "est"},
    {"code": "FI", "language": "fin"},
    {"code": "FR", "language": "fre"},
    {"code": "DE", "language": "ger"},
    {"code": "EL", "language": "gre"},
    {"code": "HU", "language": "hun"},
    {"code": "IT", "language": "ita"},
    {"code": "JA", "language": "jap"},
    {"code": "LV", "language": "lat"},
    {"code": "LT", "language": "lit"},
    {"code": "PL", "language": "pol"},
    {"code": "PT", "language": "por"},
    {"code": "RO", "language": "rom"},
    {"code": "RU", "language": "rus"},
    {"code": "SK", "language": "slk"},
    {"code": "SL", "language": "sln"},
    {"code": "ES", "language": "spa"},
    {"code": "SV", "language": "swe"},
]


def create_abbreviations_dictionary(languages=SUPPORTED_LANGUAGES):
    short_dict = {language["code"].lower(): language["code"]
                  for language in languages}
    verbose_dict = {
        language["language"].lower(): language["code"] for language in languages
    }
    return {**short_dict, **verbose_dict}


def abbreviate_language(language, engine = 'bing'):
    language = language.lower()
    abbreviations = create_abbreviations_dictionary()
    lang_token = abbreviations.get(language.lower()).lower()
    if engine == 'baidu':
        lang_token = abbreviations.get(language.lower())

    return lang_token

def auto_add_fontsize_to_subs_textline(text: str, video_type: str) -> int:
    textline_limit_size_384x288 = {
        "movie": {
            "24": 28, "57": 9,
            "25": 27, "56": 9,
            "26": 26, "55": 10,
            "27": 25, "54": 10,
            "28": 24, "53": 11,
            "29": 23, "52": 11,
            "30": 22, "51": 12,
            "31": 22, "50": 12,
            "32": 21, "49": 13,
            "33": 21, "48": 13,
            "34": 20, "47": 14,
            "35": 20, "46": 14,
            "36": 19, "45": 15,
            "37": 19, "44": 15,
            "38": 18, "43": 16,
            "39": 18, "42": 16,
            "40": 17, "41": 17,
        },
         "tv": {
            "17": 27,
            "18": 26, 
            "19": 25, 
            "20": 24, 
            "21": 23, 
            "22": 22, 
            "23": 21, 
            "24": 20, "57": 9,
            "25": 19, "56": 9,
            "26": 19, "55": 9,
            "27": 18, "54": 9,
            "28": 18, "53": 9,
            "29": 17, "52": 9,
            "30": 17, "51": 10,
            "31": 16, "50": 10,
            "32": 16, "49": 10,
            "33": 15, "48": 10,
            "34": 15, "47": 10,
            "35": 14, "46": 11,
            "36": 14, "45": 11,
            "37": 13, "44": 11,
            "38": 13, "43": 11,
            "39": 13, "42": 12,
            "40": 12, "41": 12,
        },
    }

    line_str_size = 0
    line_str_len = len(text.encode('utf-8'))
    ret = 0

    if line_str_len >= 3*28:
        gap: int = (line_str_len/3 - 28)/3
        line_str_size = 18 - 1*gap
    elif line_str_len >= 3*20:
        gap: int = (line_str_len/3 - 21)/2
        line_str_size = 24 - 2*gap
    if video_type == 'movie':
        if line_str_len >= 3*24 and line_str_len <= 3*57:
            line_str_size = textline_limit_size_384x288[video_type][str(math.ceil(line_str_len/3))]
        else:
            line_str_size = 8

        if line_str_len >= 3*24:
            ret = line_str_size
    else:
        if line_str_len >= 3*17 and line_str_len <= 3*57:
            line_str_size = textline_limit_size_384x288[video_type][str(math.ceil(line_str_len/3))]
        else:
            line_str_size = 8

        if line_str_len >= 3*17:
            ret = line_str_size
    return ret
