# import argument and option parsing
from sys import argv
from optparse import OptionParser
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

    def __init__(self, years = 5):
        # feed history, default is 5 years
        self.years = years 
        # get a random 5 digit integer
        self.rand_ext = random.randint(10000, 99999)
        # set the filename for the generated class
        self.filename = "/tmp/conversion_recipe_%s.recipe" % self.rand_ext

    def generate( self, title, url ):
        # write out file with klass string as contents
        klass = """
class BatchConversionRecipe(BasicNewsRecipe):
    title   = u'%s'
    oldest_article = (365 * %d)
    max_articles_per_feed = 100
    auto_cleanup = True
    feeds = [(u'%s', u'%s')]

""" % (title, self.years, title, url)

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
script, url = argv
# ARGS
# url

parser = OptionParser()
# options:
parser.add_option("-t","--title", action="store", type="string", dest="title", default="hostname+salt")
parser.add_option("-s", "--test", action="store_true", dest="test")
parser.add_option("-v", "--verbose", action="store_true", dest="verbose")

# create a RecipeGenerator object and write out the file for calibre,
# store the filename in the variable.
recipe_file = RecipeGenerator().generate( title, url )

# TODO: put all the code below into the RecipeGenerator class so it can be
# threaded.

# call regex to replace all non alphanumeric chars in title with _
# Erhhh mah gherrrd, Unicode
# http://stackoverflow.com/questions/11689223/python-utf-8-filesystem-iso-8859-1-files
title = re.sub("[^a-zA-Z0-9]", "_", title)

# generate the filename of the ebook
epub = "%s.epub" % title

# prepend absolute path to ebook filename
epub = "/tmp/ebooks/%s" % epub

if ( verbose ):
    verbose = "-v -v"

if ( test ):
    test = "--test"

# pass arguments to the ebook-convert program and store the string to be
# eval'd: JACK BAUER!
system_string_with_args = "ebook-convert %s %s %s %s" % (recipe_file, ensure_dir(epub), verbose, test)

# Eval the string. Do all the work!
system(system_string_with_args)
