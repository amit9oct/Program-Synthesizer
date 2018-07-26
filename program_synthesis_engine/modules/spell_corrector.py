import httplib, urllib, json


class spell_corrector:
    """
    Takes a work/phrase/sentence as input and returns
    corrected value
    """

    def __init__(self):
        """do nothing"""

    def spell_correct(self, to_correct):
        return


class bing_spell_corrector(spell_corrector):
    """
    Uses bing APIs to correct spellings of words
    """

    hostName = "api.cognitive.microsoft.com"
    apiPath = "/bing/v7.0/spellcheck?"
    apiParams = "mkt=en-us&mode=proof"

    apiKey1 = "<some-key>"
    apiKey2 = "<some-key>"

    def spell_correct(self, to_correct):
        if bing_spell_corrector.apiKey1 == "<some-key>":
            raise Exception("Set Bing's spell check api keys")
        data = urllib.urlencode({'text': to_correct})
        conn = httplib.HTTPSConnection(bing_spell_corrector.hostName)

        headers = {'Ocp-Apim-Subscription-Key': bing_spell_corrector.apiKey1,
                   'Content-Type': 'application/x-www-form-urlencoded'}
        conn.request("POST", bing_spell_corrector.apiPath, data, headers)
        response = json.loads(conn.getresponse().read())
        if (not response["flaggedTokens"]):
            return to_correct
        if (not response["flaggedTokens"][0]["suggestions"]):
            return to_correct
        return response["flaggedTokens"][0]["suggestions"][0]["suggestion"]


def __main__():
    corrector = bing_spell_corrector()
    print corrector.spell_correct("companyname")
    print corrector.spell_correct("laptpo")
    print corrector.spell_correct("approxAge")
    print corrector.spell_correct("internalMemory")
    print corrector.spell_correct("RAMSize")

#__main__()
