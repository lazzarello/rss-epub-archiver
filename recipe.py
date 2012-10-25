# Generate a recipe for calibre to convert a news feed. Imported by
# rss-ebook-archive and called if there is no existing recipe for the
# feed passed to the script

import random

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
