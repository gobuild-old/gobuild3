#!/usr/bin/python
"""
Copyright 2012 David Garcia Garzon

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

__doc__ = """\
This module provides functions to convert terminal output including
ansi terminal codes to stylable html.

The main entry point are 'deansi(input)' which performs the conversion
on an input string and 'styleSheet' which provides a minimal style sheet.
You can overwrite stylesheets by placing new rules after this minimal one.
"""

# TODO: Support empty m, being like 0m
# TODO: Support 38 and 38 (next attrib is a 256 palette color (xterm?))
# TODO: Support 51-55 decorations (framed, encircled, overlined, no frame/encircled, no overline)

import re
import cgi

colorCodes = {
    0 : 'black',
    1 : 'red',
    2 : 'green',
    3 : 'yellow',
    4 : 'blue',
    5 : 'magenta',
    6 : 'cyan',
    7 : 'white',
}
attribCodes = {
    1 : 'bright',
    2 : 'faint',
    3 : 'italic',
    4 : 'underscore',
    5 : 'blink',
# TODO: Chek that 6 is ignored on enable and disable or enable it
#    6 : 'blink_rapid',
    7 : 'reverse',
    8 : 'hide',
    9 : 'strike',
}

variations = [ # normal, pale, bright
    ('black', 'black', 'gray'), 
    ('red', 'darkred', 'red'), 
    ('green', 'darkgreen', 'green'), 
    ('yellow', 'orange', 'yellow'), 
    ('blue', 'darkblue', 'blue'), 
    ('magenta', 'purple', 'magenta'), 
    ('cyan', 'darkcyan', 'cyan'), 
    ('white', 'lightgray', 'white'), 
]

def styleSheet(brightColors=True) :
    """\
    Returns a minimal css stylesheet so that deansi output 
    could be displayed properly in a browser.
    You can append more rules to modify this default
    stylesheet.

    brightColors: set it to False to use the same color
        when bright attribute is set and when not.
    """

    simpleColors = [
        ".ansi_%s { color: %s; }" % (normal, normal)
        for normal, pale, bright in variations]
    paleColors = [
        ".ansi_%s { color: %s; }" % (normal, pale)
        for normal, pale, bright in variations]
    lightColors = [
        ".ansi_bright.ansi_%s { color: %s; }" % (normal, bright)
        for normal, pale, bright in variations]
    bgcolors = [
        ".ansi_bg%s { background-color: %s; }" % (normal, normal)
        for normal, pale, bright in variations]

    attributes = [
        ".ansi_bright { font-weight: bold; }",
        ".ansi_faint { opacity: .5; }",
        ".ansi_italic { font-style: italic; }",
        ".ansi_underscore { text-decoration: underline; }",
        ".ansi_blink { text-decoration: blink; }",
        ".ansi_reverse { border: 1pt solid; }",
        ".ansi_hide { opacity: 0; }",
        ".ansi_strike { text-decoration: line-through; }",
    ]

    return '\n'.join(
        [ ".ansi_terminal { white-space: pre; font-family: monospace; }", ]
        + (paleColors+lightColors if brightColors else simpleColors)
        + bgcolors
        + attributes
        )

def ansiAttributes(block) :
    """Given a sequence "[XX;XX;XXmMy Text", where XX are ansi 
    attribute codes, returns a tuple with the list of extracted
    ansi codes and the remaining text 'My Text'"""

    attributeRe = re.compile( r'^[[](\d+(?:;\d+)*)?m')
    match = attributeRe.match(block)
    if not match : return [], block
    if match.group(1) is None : return [0], block[2:]
    return [int(code) for code in match.group(1).split(";")], block[match.end(1)+1:]


def ansiState(code, attribs, fg, bg) :
    """Keeps track of the ansi attribute state given a new code"""

    if code == 0 : return set(), None, None   # reset all
    if code == 39 : return attribs, None, bg   # default fg
    if code == 49 : return attribs, fg, None   # default bg
    # foreground color
    if code in xrange(30,38) :
        return attribs, colorCodes[code-30], bg
    # background color
    if code in xrange(40,48) :
        return attribs, fg, colorCodes[code-40]
    # attribute setting
    if code in attribCodes :
        attribs.add(attribCodes[code])
    # attribute resetting
    if code in xrange(21,30) and code-20 in attribCodes :
        toRemove = attribCodes[code-20] 
        if toRemove in attribs :
            attribs.remove(toRemove)
    return attribs, fg, bg


def stateToClasses(attribs, fg, bg) :
    """Returns css class names given a given ansi attribute state"""

    return " ".join(
        ["ansi_"+attrib for attrib in sorted(attribs)]
        + (["ansi_"+fg] if fg else [])
        + (["ansi_bg"+bg] if bg else [])
        )

def deansi(text) :
    text = cgi.escape(text)
    blocks = text.split("\033")
    state = set(), None, None
    ansiBlocks = blocks[:1]
    for block in blocks[1:] :
        attributeCodes, plain = ansiAttributes(block)
        for code in attributeCodes : state = ansiState(code, *state)
        classes = stateToClasses(*state)
        ansiBlocks.append(
            (("<span class='%s'>"%classes) + plain + "</span>")
            if classes else plain
            )
    text = "".join(ansiBlocks)
    return text

def convert(text):
    html_template = """\
<style>
/*.ansi_terminal { background-color: #222; color: #cfc; }*/
%s
</style>
<div class='ansi_terminal'>%s</div>
"""
    return html_template % (styleSheet(), deansi(text))




if __name__ == "__main__" :
    import sys
    html_template = """\
<style>
/*.ansi_terminal { background-color: #222; color: #cfc; }*/
%s
</style>
<div class='ansi_terminal'>%s</div>
"""

#    html_template = '<style .ansi_terminal{color:#cfc} %s></style><div class="ansi_terminal">%s</div>'

    inputFile = file(sys.argv[1]) if sys.argv[1:] else sys.stdin
    print html_template % (styleSheet(), deansi(inputFile.read()))
    sys.exit(0)

