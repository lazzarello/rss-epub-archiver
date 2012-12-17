# import argument and option parsing
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
# import a url parser
from urlparse import urlparse
# import the datetime types
from datetime import date

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

# because I'm too lazy to do scope correctly
title = ""
verbose = ""
test = ""
cover_image = ""

# unpack user supplied arguments
parser = argparse.ArgumentParser(description="rip some epubs")
parser.add_argument("url", metavar="url", nargs=1, help="A full URL of a data feed")
parser.add_argument("-t","--title", action="store", dest="title", help="the title of the book (default: url hostname)")
parser.add_argument("-s", "--test", action="store_true", dest="test", help="run in test mode")
parser.add_argument("-v", "--verbose", action="store_true", dest="verbose", help="verbose output for debugging")
parser.add_argument("-d", "--days", action="store", dest="days", type=int, default=7, help="the number of days prior to start downloading posts (default: 7)")
parser.add_argument("-o","--outdir", action="store", dest="outdir", default=".", help="the directory to output the final epub file (default: current dir)")
parser.add_argument("-c", "--cover", action="store", dest="cover_image", help="the location of the cover image (file or url)")

args = parser.parse_args()

# set the title for the book
if ( not args.title ):
    title = urlparse(args.url[0]).netloc
else:
    title = args.title

# create a RecipeGenerator object and write out the file for calibre,
# store the filename in recipe_file.
recipe_file = RecipeGenerator(days=args.days).generate( title, args.url[0] )

# let's generate the output filename
# below is a discussion about the possibility for a more selective
# substitution for characters in the filename
# http://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename-in-python
prefix = re.sub("[^a-zA-Z0-9]", "_", title)

# generate the filename of the ebook
datestamp = date.today().isoformat()
epub = "/%s_%s.epub" % (prefix, datestamp)

# prepend absolute path to ebook filename
epub = args.outdir + epub

# this should probably be a case statement, and it should probably loop
# over the options hash
if ( args.verbose ):
    verbose = "-v -v"

if ( args.test ):
    test = "--test"

if ( args.cover_image ):
    cover_image = "--cover %s" % args.cover_image

# pass arguments to the ebook-convert program and store the string to be
# eval'd:
system_string_with_args = "ebook-convert %s %s %s %s %s" % (recipe_file, ensure_dir(epub), verbose, test, cover_image)

# Eval the string. Do all the work!
system(system_string_with_args)
