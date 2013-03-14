# Set up for an Ubuntu package build.
#
# This is a script because we need to set the changelog, and some day
# we may need to do something about filtering specific files so we can
# use the same skeleton for both Ubuntu and Debian builds without
# requiring them to be identical.
#
# For now, though, this just copies the debian skeleton and creates a
# changelog.

import subprocess
import shutil
import sys
import os

version = subprocess.check_output(("svnversion", "-c")).strip().split(":")[-1]

#if not version.isdigit(): sys.exit("Sources don't look pristine, not building (%r)" % version)

version = "0." + version

shutil.copytree("buildtools/debian-skeleton", "debian")

subprocess.check_call(("dch", "--create", "--package", "rpki", "--newversion",  version,
                       "Version %s of https://subvert-rpki.hactrn.net/trunk/" % version),
                      env = dict(os.environ,
                                 EDITOR   = "true",
                                 VISUAL   = "true",
                                 TZ       = "UTC",
                                 DEBEMAIL = "Rob Austein <sra@rpki.net>"))