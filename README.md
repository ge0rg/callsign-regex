# Amateur Radio Callsign RegEx generator

This tool will process ITU's [Table of International Call Sign Series](https://www.itu.int/en/ITU-R/terrestrial/fmd/Pages/call_sign_series.aspx)
in Excel format and generate the following outputs:

- [a huge RegEx](generated/callsigns.regex) that will only match valid callsigns and return the prefix as the first capture group
- [a map of prefixes to country data](generated/prefixes.pretty.json) ([dense version](generated/prefixes.dense.json))
- [a map of countries to prefixes](generated/countries.pretty.json) ([dense version](generated/countries.dense.json))

Example invocation:

```
$ ./callsign_regex.py CallSignSeriesRanges.xlsx DO1GL W100AW D3ADBEEF
DO1GL - Germany (Federal Republic of)
W100AW - United States of America
D3ADBEEF does not match
```

# Dependencies

- Python 3
- [OpenPyXL](https://openpyxl.readthedocs.io/en/stable/)


# Sources

This is based on the [callsign format description on Wikipedia](https://en.wikipedia.org/wiki/Amateur_radio_call_signs)
and on a [very helpful answer on Ham Radio Stack Exchange](https://ham.stackexchange.com/a/1360/89).

# Limitations

Several very special cases are not supported, e.g. "D9K", "C6A*" or "H2T"

# MIT License

Copyright 2022 Georg Lukas

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
