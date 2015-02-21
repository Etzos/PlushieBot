from .plugin import *

import urllib.parse
import urllib.request
import json
import re

class SearchPlugin(PlushiePlugin):
    name = "Wikipedia Access and Google Plugins"
    description = "Access and summarize English Wikipedia articles and have Plushie search Google for you"
    authors = ["Garth", "Kitsune30"]
    
    BASE_URLS = {
        # API, Wiki page
        "wikipedia": ("http://en.wikipedia.org/w/api.php", "http://en.wikipedia.org/wiki/"),
        "simple": ("http://simple.wikipedia.org/w/api.php", "http://simple.wikipedia.org/wiki/")
    }

    @plushieCmd("wiki", "wikipedia")
    @commandDoc(extra="<item to search>", doc="Has Plushie search Wikipedia for <item to search>")
    def wikiCmd(self, ctx, msg):
        result = self.getSummary(msg.noCmdMsg(), self.BASE_URLS["wikipedia"][0])
        if not result[0]:
            ctx.msg("Error: {:s}".format(result[1]), msg.replyTo)
        else:
            ctx.msg("Wikipedia entry for '{:s}': {:s} {:s}".format(
                msg.noCmdMsg(),
                result[1],
                "{:s}{:s}".format(self.BASE_URLS['wikipedia'][1], result[2].replace(" ", "_"))
                ), msg.replyTo)

    @plushieCmd("simplewiki", "sw")
    @commandDoc(extra="<item to search>", doc="Has Plushie search the Simple English Wiki for <item to search>")
    def neabWikiCmd(self, ctx, msg):
        result = self.getSummary(msg.noCmdMsg(), self.BASE_URLS["simple"][0])
        if not result[0]:
            ctx.msg("Error: {:s}".format(result[1]), msg.replyTo)
        else:
            ctx.msg("Simple English Wiki entry for '{:s}': {:s} {:s}".format(
                msg.noCmdMsg(),
                result[1],
                "{:s}{:s}".format(self.BASE_URLS['simple'][1], result[2].replace(" ", "_"))
                ), msg.replyTo)

    def getSummary(self, title, api):
        # http://en.wikipedia.org/w/api.php?action=query&prop=extracts&exchars=150&explaintext=true&titles=Earth&format=json
        params = {
            "action": "query",
            "prop": "extracts",     # Get a piece of the article
#            "exsentences": 2,       # Number of sentences to get
            "exchars": 250,         # Number of characters to get
            "exintro": "",          # Only extract the intro
            "explaintext": "",      # Only get text (no HTML)
            "format": "json",       # Output in JSON
            "redirects": "",        # Follow redirects automatically
            "generator": "search",  # Use search
            "gsrsearch": title,     # The title to search format
            "gsrnamespace": 4,      # Only search Wikipedia articles
            "gsrwhat": "nearmatch", # Search for the nearest match
            "gsrredirects": "",     # Allow redirects
            "gsrlimit": 1           # Only one result
        }
        # /w/api.php?generator=search&gsrsearch=Python%20(language)&gsrnamespace=0&gsrwhat=nearmatch&gsrredirects=&gsrlimit=1
        try:
            request = urllib.request.Request("{:s}?{:s}".format(api, urllib.parse.urlencode(params)))
            request.add_header("User-Agent", "PlushieBot Wikipedia Plugin/0.1 (supercodingmonkey@gmail.com)")
            result = urllib.request.urlopen(request)
        except:
            return (False, "Unable to connect to API.", "")
        jobj = result.read().decode('utf-8')
        jparse = json.loads(jobj)
        #print(jparse)
        if not jparse:
            return (False, "No results found.", "")
        try:
            pages = jparse['query']['pages']
            print(pages)
        except:
            return (False, "Error with query. (Talk to Garth)", "")
        for k in pages.keys():
            v = pages.get(k)
            if k == "-1":
                return (False, "No results found.", "")
            elif "extract" not in v:
                continue
            else:
                v = pages.get(k)
                bodypart = re.sub("^Coordinates: (?:.*?)\n\n", "", v["extract"])
                bodypart = bodypart.replace("\n", " ")
                return (True, bodypart, v["title"])
        return (False, "No results found.")


    @plushieCmd("google")
    @commandDoc(extra="<item to search>", doc="Has Plushie search Google for <item to search>")
    def googleStuff(self, ctx, msg):
        args = msg.getArgs()

        if len(args) < 1:
            ctx.msg("I can't google nothing.", msg.replyTo)
            return

        if len(args) > 0:
            url = urllib.parse.quote_plus(msg.noCmdMsg())
            ctx.msg("Here is the search result for '{:s}': https://www.google.com/#q={:s}".format(msg.noCmdMsg(), url), msg.replyTo)
        else:
            ctx.msg("Something has failed. Please contact Garth about it.", msg.replyTo)
