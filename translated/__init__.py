# Framework for testing translations
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

"""
Framework for running tests against translations.

Tests are loaded from modules in this directory. A test is any callable object
within the module with a name that starts with 'test_'.

Each test is called with the name of .mo file to test as an argument. A test
passes if it returns without raising an exception.
"""

import sys, tempfile, shutil, os, warnings

_tests = []

# Gather tests from this directory
import pkgutil
for finder, mod_name, _ispkg in pkgutil.iter_modules(__path__):
    # Skip __main__
    if mod_name == "__main__":
        continue

    # Load the module
    module = finder.find_module(mod_name).load_module()

    # Look for attributes that start with 'test_' and add them to the test list
    for attrname, attr in module.__dict__.items():
        if attrname.startswith('test_') and callable(attr):
            _tests.append(attr)

def testFile(mofile, prefix=None):
    """Run all registered tests against the given .mo file.

       :param str mofile: The .mo file name to check
       :param str prefix: An optional directory prefix to strip from error messages
       :return: whether the checks succeeded or not
       :rtype: bool
    """
    success = True
    for test in _tests:
        # Don't print the tmpdir path in error messages
        if prefix is not None and mofile.startswith(prefix):
            moerror = mofile[len(prefix):]
        else:
            moerror = mofile

        try:
            with warnings.catch_warnings(record=True) as w:
                test(mofile)

                # Print any warnings collected
                for warn in w:
                    print("%s warned on %s: %s" % (test.__name__, moerror, warn.message))
        except Exception as e:
            success = False
            print("%s failed on %s: %s" % (test.__name__, moerror, str(e)))

    return success

def testArchive(archive):
    """Runs all registered tests against all .mo files in the given archive.

       :param str archive: The path to an archive containing .mo files
       :return: whether the checks succeeded or not
       :rtype: bool
    """
    success = True

    archive_dir = tempfile.mkdtemp(prefix='translation-tests.')
    try:
        shutil.unpack_archive(archive, archive_dir)
        for dir, _dirnames, paths in os.walk(archive_dir):
            for mofile in (os.path.join(dir, path) for path in paths
                    if path.endswith('.mo') or path.endswith('.gmo')):
                if not testFile(mofile, prefix=archive_dir + "/"):
                    success = False
    finally:
        shutil.rmtree(archive_dir, ignore_errors=True)

    return success
