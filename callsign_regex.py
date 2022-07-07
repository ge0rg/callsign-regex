#!/usr/bin/env python3
#
# Parses prefixes and regular expressions from the ITU callsign database at
# https://www.itu.int/en/ITU-R/terrestrial/fmd/Pages/call_sign_series.aspx
#
# This follows the format described in https://en.wikipedia.org/wiki/Amateur_radio_call_signs
# however does not support several very special cases like "D9K", "C6A*" or "H2T"

import collections
import json
import openpyxl
import os
import re
import string
import sys

OUTPUT_DIR = 'generated/'

def write_utf8_file(fn, string):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    f = open(OUTPUT_DIR + fn, 'wt', encoding='utf-8')
    f.write(string)

# Extract the following info of a group from an excel row:
#
# - is_full = contains all 26 characters of the group, e.g. KAA-KAZ
# - prefix = common prefix for full group, first prefix of non-full (first and last letters will be added)
# - regex = string of the (sub)regex for this group
# - country = country that got the group allocation
def analyze_row(row):
    prefix, country = row
    first, last = prefix.value.split(" - ")
    group = { 'is_full': False, 'country': country.value, 'regex': None }
    if len(first) != 3 or len(last) != 3:
        raise ValueError("Prefixes must be 3 characters: '%s'" % prefix)
    if first[:2] != last[:2]:
        raise ValueError("Prefixes must start with the same characters: '%s'" % prefix)
    if first[2] == 'A' and last[2] == 'Z':
        group['is_full'] = True
        group['prefix'] = first[:2]
        group['regex'] = first[:2] + '[A-Z]?' # third letter is optional in full groups
    else:
        group['is_full'] = False
        group['prefix'] = first
        group['first'] = first[2]
        group['last'] = last[2]
        group['regex'] = first[:2] + '[%s-%s]' % (first[2], last[2])
    return group

def prefix_list(group):
    if group['is_full']:
        return [group['prefix']]
    else:
        return [group['prefix'][:2] + chr(ch) for ch in range(ord(group['first']), ord(group['last'])+1)]

def load_xls(fn):
    cssr = openpyxl.load_workbook(fn, data_only=True)
    sheet = cssr.worksheets[0]
    prefixes = {}
    countries = collections.defaultdict(set)
    letters = collections.Counter()
    regexes = set()
    if sheet['A1'].value != "Series" or sheet['B1'].value != "Allocated to":
        raise ValueError("Excel header mismatch")
    # load individual rows from the table and populate:
    # - prefixes (a dict of prefix->data)
    # - letters (count of the first letters' occurence in each prefix)
    # - regexes (list of alternative prefixes as regexes for latter matching)
    for row in sheet['A2':'B%d' % sheet.max_row]:
        group = analyze_row(row)
        group_prefixes = prefix_list(group)
        countries[group['country']].update(group_prefixes)
        for prefix in group_prefixes:
            prefixes[prefix] = group
        first_char = group['prefix'][0]
        letters[first_char] = letters[first_char] + 1
        del group['prefix']

    # special-case for single-letter allocations: check through the alphabet
    for first in string.ascii_uppercase:
        is_single_letter_prefix = True
        prefix = first + 'A'
        if letters[first] == 26 and prefix in prefixes and prefixes[prefix]['is_full']:
            ref = prefixes[prefix]
            for second in string.ascii_uppercase[1:]:
                prefix = first + second
                if not prefix in prefixes:
                    is_single_letter_prefix = False
                    break
                if ref['country'] != prefixes[first + second]['country']:
                    is_single_letter_prefix = False
                    break
                if not prefixes[prefix]['is_full']:
                    is_single_letter_prefix = False
                    break
            if is_single_letter_prefix:
                ref['regex'] = first + '[A-Z]{0,2}' # second and third are optional
                country = prefixes[prefix]['country']
                for second in string.ascii_uppercase:
                    del prefixes[first + second]
                    countries[country].remove(first + second)
                prefixes[first] = ref
                countries[country].add(first)
    for prefix, group in sorted(prefixes.items()):
        regexes.add(group['regex'])
    # create a regex that matches all valid callsigns and captures the country prefix
    regex_str = "(%s)[0-9][0-9A-Z]{0,3}[A-Z]" % "|".join(sorted(regexes))
    regex = re.compile(regex_str)
    write_utf8_file('callsigns.regex', regex_str + '\n')
    # store prefix map
    write_utf8_file('prefixes.dense.json', json.dumps(prefixes))
    write_utf8_file('prefixes.pretty.json', json.dumps(prefixes, indent=4))
    # convert sets to lists for JSON export and export per-country prefix lists
    countries = {key: sorted(list(val)) for key, val in countries.items()}
    write_utf8_file('countries.dense.json', json.dumps(countries))
    write_utf8_file('countries.pretty.json', json.dumps(countries, indent=4))
    return regex, prefixes


regex, prefixes = load_xls(sys.argv[1])

# test command line arguments for callsign validity
for call in sys.argv[2:]:
    call = call.upper()
    m = regex.match(call)
    if m:
        match = m.group(1)
        # find longest-matching prefix from RE capture group
        while match and not match in prefixes:
            match = match[:-1]
        if match in prefixes:
            print("%s - %s" % (call, prefixes[match]['country']))
            continue
    print("%s does not match" % call)

