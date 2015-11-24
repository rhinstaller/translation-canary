# Check translations of pango markup
#
# This will look for translatable strings that appear to contain markup and
# check that the markup in the translation matches.
#
# Copyright (C) 2015  Red Hat, Inc.
#
# This copyrighted material is made available to anyone wishing to use,
# modify, copy, or redistribute it subject to the terms and conditions of
# the GNU General Public License v.2, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY expressed or implied, including the implied warranties of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.  You should have received a copy of the
# GNU General Public License along with this program; if not, write to the
# Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.  Any Red Hat trademarks that are incorporated in the
# source code or documentation are not subject to the GNU General Public
# License and may only be used or replicated with the express permission of
# Red Hat, Inc.
#
# Red Hat Author(s): David Shea <dshea@redhat.com>

try:
    import polib
except ImportError:
    print("You need to install the python-polib package to read translations")
    raise

from pocketlint.pangocheck import is_markup, markup_match

def test_markup(mofile):
    mo = polib.mofile(mofile)

    for entry in mo.translated_entries():
        if is_markup(entry.msgid):
            # If this is a plural, check each of the plural translations
            if entry.msgid_plural:
                for plural_id, msgstr in entry.msgstr_plural.items():
                    if not markup_match(entry.msgid, msgstr):
                        raise AssertionError("Markup does not match for %d translation of msgid %s" %
                                (plural_id, entry.msgid))
            elif not markup_match(entry.msgid, entry.msgstr):
                raise AssertionError("Markup does not match for msgid %s" % entry.msgid)
