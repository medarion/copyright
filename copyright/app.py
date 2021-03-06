import copyright
import sys

class App(object):
    '''
    Interface for running app programmatically.
    '''

    def __init__(self):
        self.cli = copyright.Cli()
        self.config = copyright.Config()

    @staticmethod
    def main(argv):
        app = App()
        result = app.cli.parse(argv)
        if not result:
            return 'Failed to parse commandline.'

        return app.run()

    def process(self, file):
        langtype = self.config.lang or copyright.Detector.detect(file, self.config.autodetect)
        if not langtype:
            if self.config.debug:
                msg = 'Skipping unknown language: {0}\n'.format(file)
                sys.stdout.write(msg)
            return 0  # nothing changed

        if not self.config.dry_run:
            text = copyright.License(self.config).text
            lang = self.langs[langtype]
            commented = lang.comment(text,
                                     single=self.config.single,
                                     pad=self.config.pad)
            lf = copyright.license.LicensedFile(file, lang, commented)
            changed = lf.write(back=self.config.back, newlines=self.config.newlines)
        if not self.config.quiet:
            sys.stdout.write(file + '\n')
        return changed

    def run(self):
        self.config.load(self.cli)
        if self.config.debug:
            copyright.logger.debug("config=" + repr(self.config))

        license = self.config.license
        if license and license not in self.config.templates:
            self.cli.error("License '%s' not found. Possible values are: %r" %
                           (license, self.config.templates.keys()))

        self.langs = copyright.langs()
        walks = copyright.walks(self.config.files,
                                exclude=self.config.exclude,
                                include=self.config.include,
                                regex=self.config.regex,
                                recurse = not self.config.no_recurse,
                                debug=self.config.debug)
        changed = 0
        for walk in walks:
            for file in walk:
                if self.config.debug:
                    copyright.logger.debug("file=" + file)
                changed |= self.process(file)
        # pre-commit wants a tool to exit non-zero if any files were modified.
        return changed

def main():
    '''Run from commandline.'''
    sys.exit(App.main(sys.argv[1:]))

if '__main__' == __name__: main()

# copyright - Add or replace license boilerplate.
# Copyright (C) 2016 Remik Ziemlinski
#
# copyright is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# copyright is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
