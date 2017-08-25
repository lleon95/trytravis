#             Copyright (C) 2017 Seth Michael Larson
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

""" Send your local git repo changes to Travis CIwithout needless commits and pushes. """

import argparse
import getpass
import platform
import sys
import os
import colorama
import requests
import git


__title__ = 'trytravis'
__author__ = 'Seth Michael Larson'
__email__ = 'sethmichaellarson@protonmail.com'
__description__ = ('Send your local git repo changes to Travis CI '
                   'without needless commits and pushes.')
__license__ = 'Apache-2.0'
__url__ = 'https://github.com/SethMichaelLarson/trytravis'
__version__ = '0.0.0.dev0'

__all__ = ['main', 'TryTravis']

# Try to find the home directory for different platforms.
_home_dir = os.expanduser('~')
if _home_dir == '~' or not os.path.isdir(_home_dir):
    try:  # Windows
        import win32file
        from win32com.shell import shell, shellcon
        home = shell.SHGetFolderPath(0, shellcon.CSIDL_PROFILE, None, 0)
    except ImportError:  # Try common directories?
        for _home_dir in [os.environ.get('HOME', ''),
                          '/home/%s' % getpass.getuser(),
                          'C:\\Users\\%s' % getpass.getuser()]:
            if os.path.isdir(_home_dir):
                break

# Determine config directory.
if platform.system() == 'Windows':
    config_dir = os.path.join(_home_dir, 'trytravis')
else:
    config_dir = os.path.join(_home_dir, '.config', 'trytravis')
del _home_dir


class TryTravis(object):
    """ Object which can be used to submit jobs via `trytravis` programmatically. """
    def __init__(self, path, output=False):
        self.path = path
        self.output = output
        self.github_token = None
        self.travis_token = None
        self.remote = None
        self.build = None
        self.build_url = None
        
    def start(self, watch=False):
        self._load_personal_access_token()
        self._exchange_personal_access_token()
        self._load_trytravis_github()
        self._submit_project_to_github()
        self._wait_for_travis_build()
        if watch:
            self._watch_travis_build()
        
    def _load_personal_access_token(self)
        try:
            with open(os.path.join(config_dir, 'personal_access_token'), 'r') as f:
                self.github_token = f.read().strip()
        except (OSError, IOError):
            raise RuntimeError('ERROR: Couldn\'t load your Personal '
                               'Access Token. Run `trytravis token`.')

    def _exchange_personal_access_token(self):
        try:
            with requests.post('https://api.travis.org/auth/github',
                               headers=self._travis_headers(),
                               json={'github_token': self.github_token}) as r:
                if not r.ok:
                    raise RuntimeError('ERROR: Couldn\'t exchange your Personal Access '
                                       'Token for a Travis API token. Additional '
                                       'information: %s' % str(r.content))
                self.travis_token = r.json()['access_token']
        except requests.RequestException as e:
            raise RuntimeError('ERROR: Couldn\'t exchange your Personal Access '
                               'Token for a Travis API token. Additional information: '
                               '%s' % str(e))

    def _load_trytravis_github(self):
        raise NotImplementedError()

    def _submit_project_to_github(self):
        raise NotImplementedError()

    def _wait_for_travis_build(self):
        raise NotImplementedError()

    def _watch_travis_build(self):
        colorama.init()
        raise NotImplementedError()

    def _travis_headers(self):
        headers = {'User-Agent': 'trytravis/%s' % __version__,
                   'Accept': 'application/vnd.travis-ci.2+json',
                   'Host': 'api.travis.org'}
        if self.travis_token is not None:
            headers['Authorization'] = 'token ' + self.travis_token
        return headers


def main(argv=None):
    """ Main entry point when the user runs the `trytravis` command. """
    try:
        if argv is None:
            argv = sys.argv[1:]

        trytravis = TryTravis(os.getcwd(), output=True)
        trytravis.start(watch=True)
    finally:
        sys.stdout.write(colorama.Style.RESET_ALL)
        sys.stdout.flush()
    sys.exit(0)