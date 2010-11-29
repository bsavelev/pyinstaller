#!/usr/bin/env python
import glob
import os, sys
import shutil
import unittest

MST_DIR = os.path.abspath(os.path.dirname(sys.argv[0]))
HOME = os.path.normpath(os.path.join(MST_DIR, ".."))
MAKESPEC_EXE = os.path.join(HOME, "Makespec.py")
BUILD_EXE = os.path.join(HOME, "Build.py")
SCRIPT_FOR_TESTS = os.path.join(MST_DIR, "test.py")
LOG_FILE = os.path.join(MST_DIR, "err.log")
if os.name == "posix":
    NULL_DEV = "/dev/null"
else:
    NULL_DEV = "nul"
CLEANUP = ["build/", "dist/", "*.log", "warn*.txt", "*.py[co]", "*/*.py[co]",
           "*/*/*.py[co]", "*.spec"]
newSpecFail = "Unable to makespec test.py"
switchSpecFail = "Unable to convert test.spec"
buildFail = "Unable to build test.spec"

def clean(to_clean=CLEANUP):
    """Cleaning tests resouces"""
    for clean in to_clean:
        clean = glob.glob(clean)
        for path in clean:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)

def execute(cmd):
    retcode = os.system(cmd + " > " + NULL_DEV + " 2> " + LOG_FILE)
    errstring = "\nMore datails:\n" + open(LOG_FILE, 'r').read()
    return retcode, errstring

class MakespecTest(unittest.TestCase):
    def tearDown(self):
        clean()

    def build(self, specfile="test.spec"):
        retcode, errstring = execute("%s -y %s" % (BUILD_EXE, specfile))
        self.assertEqual(retcode, 0, buildFail + errstring)

    def makespec(self, scriptfile=SCRIPT_FOR_TESTS, dep_mode = "--onedir"):
        retcode, errstring = execute("%s %s %s" % (MAKESPEC_EXE, dep_mode, scriptfile))
        #TODO: display only errstring?
        if scriptfile.endswith(".spec"):
            self.assertEqual(retcode, 0, switchSpecFail + errstring)
        else:
            self.assertEqual(retcode, 0, newSpecFail + errstring)

    def editspec(self):
        specfile_content = open("test.spec", 'r').read()
        specfile_content = specfile_content.replace("name_of_exe = 'test'", "name_of_exe = 'edited'")
        specfile_content = specfile_content.replace("build_dir = 'build/pyi.linux2/test'", "build_dir = 'build/pyi.linux2/edited'")
        specfile_content = specfile_content.replace("useDebug = False", "useDebug = True")
        #TODO: edit more?
        open("test.spec", 'w').write(specfile_content)

    # Tests are performed from here, in alphabetical order
    def test_build_onedir(self):
        """Building onedir spec deployment"""
        self.makespec()
        self.build()

    def test_build_onefile(self):
        """Building onefile spec deployment"""
        self.makespec(dep_mode="--onefile")
        self.build()

    def test_edited_file(self):
        """Building an edited spec"""
        self.makespec()
        self.editspec()
        self.build()

    def test_switch_to_onedir(self):
        """Onefile to onedir deployment"""
        self.makespec(dep_mode="--onefile")
        self.makespec(scriptfile="test.spec")
        self.build()

    def test_switch_to_onefile(self):
        """Onedir to onefile deployment"""
        self.makespec()
        self.makespec(scriptfile="test.spec", dep_mode="--onefile")
        self.build()

    def test_switch_to_onefile_edited_file(self):
        """Switching an edited spec file"""
        self.makespec()
        self.editspec()
        self.makespec(scriptfile="test.spec", dep_mode="--onefile")
        self.build()

if __name__ == "__main__":
    os.chdir(MST_DIR)
    unittest.main()