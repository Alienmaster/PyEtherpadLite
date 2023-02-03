#!/usr/bin/env python
"""Module to talk to EtherpadLite API."""

import json
try:
    import urllib.parse as urllib_parse
    import urllib.error as urllib_error
    import urllib.request as urllib_request
    import urllib.request as build_opener
except ImportError:
    import urllib as urllib_parse
    import urllib2 as urllib_error
    import urllib2 as urllib_request
    import urllib2 as build_opener

class EtherpadLiteClient:
    """Client to talk to EtherpadLite API."""
    API_VERSION = "1.2.15"

    CODE_OK = 0
    CODE_INVALID_PARAMETERS = 1
    CODE_INTERNAL_ERROR = 2
    CODE_INVALID_FUNCTION = 3
    CODE_INVALID_API_KEY = 4
    TIMEOUT = 20

    apiKey = ""
    baseUrl = "http://localhost:9001/api"

    def __init__(self, apiKey=None, baseUrl=None):
        if apiKey:
            self.apiKey = apiKey

        if baseUrl:
            self.baseUrl = baseUrl

    def call(self, function, arguments=None):
        """Create a dictionary of all parameters"""
        url = '%s/%s/%s' % (self.baseUrl, self.API_VERSION, function)

        params = arguments or {}
        params.update({'apikey': self.apiKey})
        data = urllib_parse.urlencode(params, True)
        data = data.encode('utf-8')

        try:
            opener = build_opener.build_opener()
            request = urllib_request.Request(url=url, data=data)
            response = opener.open(request, timeout=self.TIMEOUT)
            #result = json.loads(response.readall().decode('utf-8'))
            #import pdb; pdb.set_trace()
            result = response.read().decode('utf-8')
            response.close()
        except urllib_error.HTTPError:
            raise

        #result = json.loads(result['message'])
        result = json.loads(result)
        if result is None:
            raise ValueError("JSON response could not be decoded")

        return self.handleResult(result)

    def handleResult(self, result):
        """Handle API call result"""
        if 'code' not in result:
            raise Exception("API response has no code")
        if 'message' not in result:
            raise Exception("API response has no message")

        if 'data' not in result:
            result['data'] = None

        if result['code'] == self.CODE_OK:
            return result['data']
        elif result['code'] == self.CODE_INVALID_PARAMETERS or result['code'] == self.CODE_INVALID_API_KEY:
            raise ValueError(result['message'])
        elif result['code'] == self.CODE_INTERNAL_ERROR:
            raise Exception(result['message'])
        elif result['code'] == self.CODE_INVALID_FUNCTION:
            raise Exception(result['message'])
        else:
            raise Exception("An unexpected error occurred whilst handling the response")

    # GROUPS
    # Pads can belong to a group. The padID of grouppads is starting with a groupID like g.asdfasdfasdfasdf$test

    def createGroup(self):
        """creates a new group"""
        return self.call("createGroup")

    def createGroupIfNotExistsFor(self, groupMapper):
        """this functions helps you to map your application group ids to Etherpad group ids"""
        return self.call("createGroupIfNotExistsFor", {
            "groupMapper": groupMapper
        })

    def deleteGroup(self, groupID):
        """deletes a group"""
        return self.call("deleteGroup", {
            "groupID": groupID
        })

    def listPads(self, groupID):
        """returns all pads of this group"""
        return self.call("listPads", {
            "groupID": groupID
        })

    def createGroupPad(self, groupID, padName, text=''):
        """creates a new pad in this group"""
        params = {
            "groupID": groupID,
            "padName": padName,
        }
        if text:
            params['text'] = text
        return self.call("createGroupPad", params)

    def listAllGroups(self):
        """lists all existing groups"""
        return self.call("listAllGroups")

    # AUTHORS
    # Theses authors are bind to the attributes the users choose (color and name).

    def createAuthor(self, name=''):
        """creates a new author"""
        params = {}
        if name:
            params['name'] = name
        return self.call("createAuthor", params)

    def createAuthorIfNotExistsFor(self, authorMapper, name=''):
        """this functions helps you to map your application author ids to Etherpad author ids"""
        params = {
            'authorMapper': authorMapper
        }
        if name:
            params['name'] = name
        return self.call("createAuthorIfNotExistsFor", params)

    def listPadsOfAuthor(self, authorID):
        """returns an array of all pads this author contributed to"""
        return self.call("listPadsOfAuthor", {
            "authorID": authorID
        })

    def getAuthorName(self, authorID):
        """Returns the Author Name of the author"""
        return self.call("getAuthorName", {
            "authorID": authorID
        })

    # SESSIONS
    # Sessions can be created between a group and an author. This allows an author to access more than one group. 
    # The sessionID will be set as a cookie to the client and is valid until a certain date. The session cookie can also 
    # contain multiple comma-separated sessionIDs, allowing a user to edit pads in different groups at the same time.
    # Only users with a valid session for this group, can access group pads. You can create a session after you 
    # authenticated the user at your web application, to give them access to the pads. You should save the sessionID 
    # of this session and delete it after the user logged out.

    def createSession(self, groupID, authorID, validUntil):
        """creates a new session. validUntil is an unix timestamp in seconds"""
        return self.call("createSession", {
            "groupID": groupID,
            "authorID": authorID,
            "validUntil": validUntil
        })

    def deleteSession(self, sessionID):
        """deletes a session"""
        return self.call("deleteSession", {
            "sessionID": sessionID
        })

    def getSessionInfo(self, sessionID):
        """returns informations about a session"""
        return self.call("getSessionInfo", {
            "sessionID": sessionID
        })

    def listSessionsOfGroup(self, groupID):
        """returns all sessions of a group"""
        return self.call("listSessionsOfGroup", {
            "groupID": groupID
        })

    def listSessionsOfAuthor(self, authorID):
        """returns all sessions of an author"""
        return self.call("listSessionsOfAuthor", {
            "authorID": authorID
        })

    # PAD CONTENT
    # Pad content can be updated and retrieved through the API

    def getText(self, padID, rev=None):
        """returns the text of a pad"""
        params = {"padID": padID}
        if rev is not None:
            params['rev'] = rev
        return self.call("getText", params)

    def setText(self, padID, text): #TODO New setText for Text >8KB See: https://etherpad.org/doc/v1.8.14/#index_settextpadid-text
        """Sets the text of a pad"""
        return self.call("setText", {
            "padID": padID,
            "text": text
        })
    
    def appendText(self, padID, text): #TODO New appendText for Text >8KB
        """Appends text to a pad."""
        return self.call("appendText", {
            "padID": padID,
            "text": text
        })

    def getHtml(self, padID, rev=None):
        """returns the text of a pad formatted as HTML"""
        params = {"padID": padID}
        if rev is not None:
            params['rev'] = rev
        return self.call("getHTML", params)

    def setHtml(self, padID, html): #TODO New setHTML for Text >8KB
        """sets the text of a pad based on HTML, HTML must be well-formed. Malformed HTML will send a warning to the API log."""
        return self.call("setHTML", {
            "padID": padID,
            "html": html
        })
    
    def getAttributePool(self, padID):
        """returns the attribute pool of a pad"""
        return self.call("getAttributePool", {
            "padID": padID
        })

    def getRevisionChangeset(self, padID, rev=None):
        """get the changeset at a given revision, or last revision if 'rev' is not defined."""
        params = {"padID": padID}
        if rev is not None:
            params['rev'] = rev
        return self.call("getRevisionChangeset", params)

    def createDiffHtml(self, padID, startRev, endRev):
        """returns an object of diffs from 2 points in a pad"""
        return self.call("createDiffHTML", {
            "padID": padID,
            "startRev": startRev,
            "endRev": endRev
        })

    def restoreRevision(self, padID, rev):
        """Restores revision from past as new changeset"""
        return self.call("restoreRevision", {
            "padID": padID,
            "rev": rev
        })

    # CHAT

    def getChatHistory(self, padID, start = None, end = None):
        """returns a part of the chat history, when start and end are given or the whole chat histroy, when no extra parameters are given"""
        params = {"padID": padID}
        if start is not None and end is not None:
            params['start'] = start
            params['end'] = end        
        return self.call("getChatHistory", params)

    def getChatHead(self, padID):
        """returns the chatHead (last number of the last chat-message) of the pad"""
        return self.call("getChatHead", {
            "padID": padID,
        })

    def appendChatMessage(self, padID, text, authorID, time=''):
        """creates a chat message, saves it to the database and sends it to all connected clients of this pad"""
        params = {
            "padID": padID,
            "text": text,
            "authorID": authorID
        }
        if time:
            params['time'] = time
        return self.call("appendChatMessage", params)

    # PAD
    # Group pads are normal pads, but with the name schema GROUPID$PADNAME. A security manager controls 
    # access of them and it's forbidden for normal pads to include a $ in the name.

    def createPad(self, padID, text=''):
        """creates a new (non-group) pad. Note that if you need to create a group Pad, you should call createGroupPad. 
        You get an error message if you use one of the following characters in the padID: "/", "?", "&" or "#"."""
        params = {
            "padID": padID,
        }
        if text:
            params['text'] = text
        return self.call("createPad", params)

    def getRevisionsCount(self, padID):
        """returns the number of revisions of this pad"""
        return self.call("getRevisionsCount", {
            "padID": padID
        })

    def getSavedRevisionsCount(self, padID):
        """returns the number of saved revisions of this pad"""
        return self.call("getSavedRevisionsCount", {
            "padID": padID
        })

    def listSavedRevisions(self, padID):
        """returns the list of saved revisions of this pad"""
        return self.call("listSavedRevisions", {
            "padID": padID
        })

    def saveRevision(self, padID, rev=''):
        """saves a revision"""
        params = {
            'padID': padID
        }
        if rev:
            params['rev'] = rev
        return self.call("saveRevision", params)

    def padUsersCount(self, padID):
        """returns the number of users currently editing this pad"""
        return self.call("padUsersCount", {
            "padID": padID
        })

    def padUsers(self, padID):
        """returns the list of users that are currently editing this pad"""
        return self.call("padUsers", {
            "padID": padID
        })

    def deletePad(self, padID):
        """deletes a pad"""
        return self.call("deletePad", {
            "padID": padID
        })

    def copyPad(self, sourceID, destinationID, force=False):
        """copies a pad with full history and chat. If force is true and the destination pad exists, it will be overwritten."""
        params = {
            "sourceID": sourceID,
            "destinationID": destinationID,
            "force": force
        }
        return self.call("copyPad", params)

    def copyPadWithoutHistory(self, sourceID, destinationID, force=False):
        """copies a pad without copying the history and chat. If force is true and the destination pad exists, it will be 
        overwritten. Note that all the revisions will be lost! In most of the cases one should use copyPad API instead."""
        params = {
            "sourceID": sourceID,
            "destinationID": destinationID,
            "force": force
        }
        return self.call("copyPadWithoutHistory", params)

    def movePad(self, sourceID, destinationID, force=False):
        """moves a pad. If force is true and the destination pad exists, it will be overwritten."""
        params = {
            "sourceID": sourceID,
            "destinationID": destinationID,
            "force": force
        }
        return self.call("movePad", params)

    def getReadOnlyID(self, padID):
        """returns the read only link of a pad"""
        return self.call("getReadOnlyID", {
            "padID": padID
        })

    def getPadID(self, readOnlyID):
        """returns the id of a pad which is assigned to the readOnlyID"""
        return self.call("getPadID", {
            "readOnlyID": readOnlyID
        })

    def setPublicStatus(self, padID, publicStatus):
        """sets a boolean for the public status of a pad"""
        return self.call("setPublicStatus", {
            "padID": padID,
            "publicStatus": publicStatus
        })

    def getPublicStatus(self, padID):
        """return true of false"""
        return self.call("getPublicStatus", {
            "padID": padID
        })

    def listAuthorsOfPad(self, padID):
        """returns the ids of all authors who've edited this pad"""
        return self.call("listAuthorsOfPad", {
            "padID": padID
        })

    def getLastEdited(self, padID):
        """returns the timestamp of the last revision of the pad"""
        return self.call("getLastEdited", {
            "padID": padID
        })
    
    def sendClientsMessage(self, padID, msg):
        """sends a custom message of type msg to the pad"""
        return self.call("sendClientsMessage", {
            "padID": padID,
            "msg": msg
        })

    def checkToken(self):
        """returns ok when the current api token is valid"""
        return self.call("checkToken", {
            "checkToken": padID
        })

    def setPassword(self, padID, password): #TODO Depricated?
        """returns ok or a error message"""
        return self.call("setPassword", {
            "padID": padID,
            "password": password
        })

    def isPasswordProtected(self, padID): #TODO Depricated?
        """returns true or false"""
        return self.call("isPasswordProtected", {
            "padID": padID
        })

    # PADS
    
    def listAllPads(self):
        """lists all pads on this epl instance"""
        return self.call("listAllPads")

    # GLOBAL

    def getStats(self):
        """get stats of the etherpad instance"""
        return self.call("getStats")
