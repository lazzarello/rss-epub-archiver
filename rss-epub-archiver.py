# import argument and option parsing
from sys import argv
import argparse
# import exit codes
from sys import exit
# import regular expressions
import re
# import filesystem functions
import os
# not sure why I have to repeat this for the system() function
from os import system
# import random number generator
import random

# define the class to generate the conversion code for calibre
class RecipeGenerator(object):

    def __init__(self, days = 7):
        # feed history, default is 7 days
        self.days = days
        # get a random 5 digit integer
        self.rand_ext = random.randint(10000, 99999)
        # set the filename for the generated class
        self.filename = "/tmp/conversion_recipe_%s.recipe" % self.rand_ext

    def generate( self, title, url ):
        # write out file with klass string as contents
        klass = """
class BatchConversionRecipe(BasicNewsRecipe):
    title   = u'%s'
    oldest_article = %d
    max_articles_per_feed = 100
    auto_cleanup = True
    feeds = [(u'%s', u'%s')]

""" % (title, self.days, title, url)

        recipe = open(self.filename, 'w')
        recipe.write(klass)
        recipe.close()

        # return the full path to the file as a string
        return self.filename

# function to automatically create a directory if it doesn't exist
# http://stackoverflow.com/questions/273192/python-best-way-to-create-directory-if-it-doesnt-exist-for-file-write
def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)
    return f

# check that the ebook-convert binary is installed, if not bail with
# some helpful output
if (system("which ebook-convert") > 0):
    output = '''
You do not have the ebook-convert binary installed.  Please install the
Calibre application on your operating system.  If you run Ubuntu, run
"sudo apt-get install calibre".  If you run MacOS X and have already
installed Calibre, you must enable this utility by going to Preferences
-> Miscellaneous -> Install command line tools
'''
    print output
    exit(1)

# unpack arguments
parser = argparse.ArgumentParser(description="rip some epubs")
parser.add_argument("url", metavar="url", nargs=1)
parser.add_argument("-t","--title", action="store", dest="title", default="hostname+salt", help="the title of the book (default: hostname+salt)")
parser.add_argument("-s", "--test", action="store_true", dest="test", help="run in test mode")
parser.add_argument("-v", "--verbose", action="store_true", dest="verbose", help="verbose output for debugging")
parser.add_argument("-d", "--days", action="store", dest="days", type=int, help="the number of days prior to start downloading posts")
parser.add_argument("-o","--outdir", action="store", dest="outdir", default=".", help="the directory to output the final epub file (default: current dir)")
args = parser.parse_args()

# create a RecipeGenerator object and write out the file for calibre,
# store the filename in the variable.
recipe_file = RecipeGenerator().generate( args.title, args.url[0] )

# call regex to replace all non alphanumeric chars in title with _
# Erhhh mah gherrrd, Unicode
# http://stackoverflow.com/questions/11689223/python-utf-8-filesystem-iso-8859-1-files
title = re.sub("[^a-zA-Z0-9]", "_", args.title)

# generate the filename of the ebook
epub = "/%s.epub" % title

# prepend absolute path to ebook filename
epub = args.outdir + epub

verbose = ""
test = ""

if ( args.verbose ):
    verbose = "-v -v"

if ( args.test ):
    test = "--test"

# pass arguments to the ebook-convert program and store the string to be
# eval'd: JACK BAUER!
system_string_with_args = "ebook-convert %s %s %s %s" % (recipe_file, ensure_dir(epub), verbose, test)

print system_string_with_args
# Eval the string. Do all the work!
system(system_string_with_args)
