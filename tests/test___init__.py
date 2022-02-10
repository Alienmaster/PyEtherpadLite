# !/usr/bin/env python
"""Module to test py_etherpad."""

import urllib3
import urllib.error as urllib_error
import PyEtherpad
import unittest
import random
import string

apiKey = "ef4d13df379edf92f2d2011add171980e59092830a89b62c66a55b914f72dceb"
baseUrl = "http://localhost:9001/api"


class TestEtherpadLiteClient(unittest.TestCase):
    """Class to test EtherpadLiteClient."""

    def setUp(self):
        self.standard_content = 'Welcome to Etherpad!\n\nThis pad text is synchronized as you type, so that everyone ' \
                           'viewing this page sees the same text. This allows you to collaborate seamlessly on ' \
                           'documents!\n\nGet involved with Etherpad at https://etherpad.org\n\nWarning: DirtyDB is ' \
                           'used. This is not recommended for production. -- To suppress these warning messages ' \
                           'change suppressErrorsInPadText to true in your settings.json\n\n'

        with open('tests/loremIpsum.txt') as f:
            self.loremIpsum = f.read()

        self.pad_id = 'meow'

        self.text = 'Maumau mau maumaumau Mau!'

        """Assign a shared EtherpadLiteClient instance to self."""
        self.ep_client = PyEtherpad.EtherpadLiteClient(apiKey, baseUrl)

    # GROUPS

    def testGroups(self):
        """list, create and delete Groups"""
        # self.ep_client.deleteGroup(["g.af5lNoycwwlAG6Q7"])
        self.assertEqual(self.ep_client.listAllGroups(), {'groupIDs': []})
        group = self.ep_client.createGroup()["groupID"]
        self.assertEqual(self.ep_client.listAllGroups(), {'groupIDs': [group]})
        self.assertEqual(self.ep_client.deleteGroup(group), None)
        self.assertEqual(self.ep_client.listAllGroups(), {'groupIDs': []})

        # Delete non-existing group
        with self.assertRaises(ValueError) as cm:
            self.ep_client.deleteGroup(group)
        self.assertEqual(str(cm.exception), 'groupID does not exist')

    def testGroupMapper(self):
        """Test Group Mapper. Create two groups with mapping to external ID.

        Create group one and try to create the same group another time.
        Create a second group, remove the first and remove the second afterwards."""

        e_group_id_one = "Cat Pack"
        e_group_id_two = "Feline Pack"
        # Create first group with "Cat Pack" and check if it exists only once
        i_group_id_one = self.ep_client.createGroupIfNotExistsFor(e_group_id_one)
        self.assertEqual(self.ep_client.listAllGroups(), {'groupIDs': [i_group_id_one["groupID"]]})
        self.assertEqual(self.ep_client.createGroupIfNotExistsFor(e_group_id_one), i_group_id_one)
        self.assertEqual(self.ep_client.createGroupIfNotExistsFor(e_group_id_one), i_group_id_one)
        self.assertEqual(self.ep_client.listAllGroups(), {'groupIDs': [i_group_id_one["groupID"]]})

        # Create second group with "Feline Pack" and check if both groups exist.
        i_group_id_two = self.ep_client.createGroupIfNotExistsFor(e_group_id_two)
        self.assertEqual(self.ep_client.listAllGroups(),
                         {'groupIDs': [i_group_id_one["groupID"], i_group_id_two["groupID"]]})

        # Try to create the same group another time
        self.assertEqual(self.ep_client.createGroupIfNotExistsFor(e_group_id_two), i_group_id_two)
        self.assertEqual(self.ep_client.createGroupIfNotExistsFor(e_group_id_two), i_group_id_two)

        # Delete the first group
        self.assertEqual(self.ep_client.deleteGroup(i_group_id_one["groupID"]), None)
        self.assertEqual(self.ep_client.listAllGroups(), {'groupIDs': [i_group_id_two["groupID"]]})

        # Delete the second group
        self.assertEqual(self.ep_client.deleteGroup(i_group_id_two["groupID"]), None)
        self.assertEqual(self.ep_client.listAllGroups(), {'groupIDs': []})

    def testCreateGroupPad(self):
        pad_name_one = 'Hairball'
        pad_name_two = 'Paws'

        pad_content_two = 'Wo lebt eine Katze? Im Miezhaus'

        # Create groups
        group_one = self.ep_client.createGroup()['groupID']
        group_two = self.ep_client.createGroup()['groupID']
        self.assertEqual(self.ep_client.listAllGroups(), {'groupIDs': [group_one, group_two]})

        # Create empty group Pad for group one and list group Pads
        # TODO:Mismatch between Doc and API? Return not Null of "createGroupPad" PR running
        pad_id_one = group_one + "$" + pad_name_one
        self.assertEqual(self.ep_client.createGroupPad(group_one, pad_name_one), {'padID': pad_id_one})
        self.assertEqual(self.ep_client.listPads(group_one), {'padIDs': [pad_id_one]})
        self.assertEqual(self.ep_client.listPads(group_two), {'padIDs': []})

        # Create prefilled Pad for group two and list group Pads
        pad_id_two = group_two + "$" + pad_name_two
        self.assertEqual(self.ep_client.createGroupPad(group_two, pad_name_two, pad_content_two), {'padID': pad_id_two})

        # Check if both groups have one pad each
        self.assertEqual(self.ep_client.listPads(group_one), {'padIDs': [pad_id_one]})
        self.assertEqual(self.ep_client.listPads(group_two), {'padIDs': [pad_id_two]})

        # Create the same pad another time
        # TODO:PR Running pad =/= padName
        with self.assertRaises(ValueError) as cm:
            self.ep_client.createGroupPad(group_one, pad_name_one)
        self.assertEqual(str(cm.exception), 'padName does already exist')

        # Read both group Pads
        self.assertEqual(self.ep_client.getText(pad_id_one), {'text': self.standard_content})
        self.assertEqual(self.ep_client.getText(pad_id_two), {'text': pad_content_two + "\n"})

        # Delete Pads
        self.assertEqual(self.ep_client.deletePad(pad_id_one), None)
        self.assertEqual(self.ep_client.listPads(group_one), {'padIDs': []})
        self.assertEqual(self.ep_client.listPads(group_two), {'padIDs': [pad_id_two]})
        self.assertEqual(self.ep_client.deletePad(pad_id_two), None)
        self.assertEqual(self.ep_client.listPads(group_two), {'padIDs': []})

        # Delete groups
        self.assertEqual(self.ep_client.deleteGroup(group_one), None)
        self.assertEqual(self.ep_client.deleteGroup(group_two), None)
        self.assertEqual(self.ep_client.listAllGroups(), {'groupIDs': []})

        # Create Pad for non-existing group
        with self.assertRaises(ValueError) as cm:
            self.ep_client.createGroupPad(group_one, pad_name_one)
        self.assertEqual(str(cm.exception), 'groupID does not exist')

    # AUTHORS

    def testCreateAuthor(self):
        # TODO:missing Test of listOfPadsOfAuthor when Authors has a Pad
        # Docs wrong: getAuthorName returns String of authorName not Dict
        # See Issue: https://github.com/ether/etherpad-lite/issues/5410

        # Create an author
        random_name_one = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(16))
        random_name_two = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(16))

        author_id_one = self.ep_client.createAuthor(random_name_one)

        # get author name
        self.assertEqual(self.ep_client.getAuthorName(author_id_one['authorID']), random_name_one)
        print(self.ep_client.getAuthorName(author_id_one['authorID']))

        # Create another with authormapper with empty name and check name of both authors
        author_id_two = self.ep_client.createAuthorIfNotExistsFor('')
        self.assertEqual(self.ep_client.getAuthorName(author_id_two['authorID']), None)
        self.assertEqual(self.ep_client.getAuthorName(author_id_one['authorID']), random_name_one)

        # Try to create the first author again with authormapper
        self.assertNotEqual(self.ep_client.createAuthorIfNotExistsFor(random_name_one),
                            {'authorID': author_id_one['authorID']})

        # Check authors empty padlist and create a pad
        self.assertEqual(self.ep_client.listPadsOfAuthor(author_id_one['authorID']), {'padIDs': []})

        # Check pads of non-existing author
        with self.assertRaises(ValueError) as cm:
            self.ep_client.listPadsOfAuthor('a.' + random_name_two)
        self.assertEqual(str(cm.exception), 'authorID does not exist')

        # Check pads of non valid authorID
        with self.assertRaises(ValueError) as cm:
            self.ep_client.listPadsOfAuthor(random_name_two)
        self.assertEqual(str(cm.exception), 'parameter authorID is in a wrong format')

    # SESSIONS

    # PAD CONTENT

    # CHAT

    def testChat(self):
        pad_id = 'tobbe'

        # Create Pad and Author
        self.assertEqual(self.ep_client.listAllPads(), {'padIDs': []})
        self.assertEqual(self.ep_client.createPad(pad_id), None)
        self.assertEqual(self.ep_client.listAllPads(), {'padIDs': [pad_id]})
        author_id = self.ep_client.createAuthor("Der gestiefelte Kater")['authorID']

        # Append chat message, check head and check messages
        self.assertEqual(self.ep_client.getChatHead(pad_id), {'chatHead': -1})
        self.assertEqual(self.ep_client.appendChatMessage
                         (pad_id, "hello World", author_id), None)
        # self.assertEqual(self.ep_client.getChatHead(pad_id), {'chatHead': 0})
        print(self.ep_client.getChatHistory(pad_id))

        # Append chat message with timestamp
        self.assertEqual(self.ep_client.appendChatMessage
                         (pad_id, "The sense of life is: ", author_id, 0), None)
        # self.assertEqual(self.ep_client.getChatHead(pad_id), {'chatHead': 1})

        print(self.ep_client.getChatHistory(pad_id))

        # appendChatMessage(padID, text, authorID[, time])
        # Check head of non-existing pad
        pad_id_invalid = 'unknown'
        with self.assertRaises(ValueError) as cm:
            self.ep_client.getChatHead(pad_id_invalid)
        self.assertEqual(str(cm.exception), 'padID does not exist')

        # Delete Pad
        self.assertEqual(self.ep_client.deletePad(pad_id), None)

    # def getChatHistory(self, padID, start = None, end = None):

    # PAD

    def testCreateAndDeletePad(self):
        """Test Create and Delete Pad"""
        pad_id = 'Otocolobus manul'
        texts = [None, self.text, self.loremIpsum]

        for text in texts:
            # Create Pad, check Text (with and without) and delete Pad
            self.assertEqual(self.ep_client.listAllPads(), {'padIDs': []})
            self.assertEqual(self.ep_client.createPad(pad_id, text), None)
            self.assertEqual(self.ep_client.listAllPads(), {'padIDs': [pad_id.replace(" ", "_")]})
            if text:
                self.assertEqual(self.ep_client.getText(pad_id.replace(" ", "_"))['text'], text + '\n')
            else:
                self.assertEqual(self.ep_client.getText(pad_id.replace(" ", "_"))['text'], self.standard_content)
            self.assertEqual(self.ep_client.deletePad(pad_id), None)
            self.assertEqual(self.ep_client.listAllPads(), {'padIDs': []})

        # Create Pad with same ID once again
        self.assertEqual(self.ep_client.createPad(pad_id), None)
        with self.assertRaises(ValueError) as cm:
            self.ep_client.createPad(pad_id)
        self.assertEqual(str(cm.exception), 'padID does already exist')
        self.assertEqual(self.ep_client.deletePad(pad_id), None)

        # Create Pad with invalid character
        pad_ids_inv = ['F&CK', 'meow?', '#catlife', '/bowl/food']

        for inv_id in pad_ids_inv:
            with self.assertRaises(ValueError) as cm:
                self.ep_client.createPad(inv_id)
            self.assertEqual(str(cm.exception), 'malformed padID: Remove special characters')

        # Check if all pads removed
        self.assertEqual(self.ep_client.listAllPads(), {'padIDs': []})

    def testRevisions(self):
        """Create a pad, change the pad and save the revision"""
        # TODO:Test 8KB Text
        # TODO:Append Text
        # TODO:Append Text 8KB
        pad_id = self.pad_id
        text = self.text

        # Create pad
        self.assertEqual(self.ep_client.createPad(pad_id), None)
        self.assertEqual(self.ep_client.listAllPads(), {'padIDs': [pad_id]})

        # Check revision, set and append text and check again
        self.assertEqual(self.ep_client.getRevisionsCount(pad_id), {'revisions': 0})
        self.assertEqual(self.ep_client.setText(pad_id, text), None)
        self.assertEqual(self.ep_client.getRevisionsCount(pad_id), {'revisions': 1})
        self.assertEqual(self.ep_client.appendText(pad_id, text), None)
        self.assertEqual(self.ep_client.getRevisionsCount(pad_id), {'revisions': 2})

        # Check revision on non-existing pad
        with self.assertRaises(ValueError) as cm:
            self.ep_client.getRevisionsCount('Pussycat')
        self.assertEqual(str(cm.exception), 'padID does not exist')

        # Save revision and list revisions
        self.assertEqual(self.ep_client.listSavedRevisions(pad_id), {'savedRevisions': []})
        self.assertEqual(self.ep_client.saveRevision(pad_id), None)
        self.assertEqual(self.ep_client.listSavedRevisions(pad_id), {'savedRevisions': [2]})

        # Delete pad
        self.assertEqual(self.ep_client.deletePad(pad_id), None)

    def testPublicStatus(self):
        # Public Status depends to a group membership
        # msg "You can only get/set the publicStatus of pads that belong to a group"
        pad_name = self.pad_id
        
        # Create group
        self.assertEqual(self.ep_client.listAllGroups(), {'groupIDs': []})
        # print(self.ep_client.createGroup())
        group_id = self.ep_client.createGroup()["groupID"]
        self.assertEqual(self.ep_client.listAllGroups(), {'groupIDs': [group_id]})

        # Create empty group pad
        pad_id = group_id + "$" + pad_name
        self.assertEqual(self.ep_client.createGroupPad(group_id, pad_name), {'padID': pad_id})

        # Get public status and set public status
        self.assertEqual(self.ep_client.getPublicStatus(pad_id), {'publicStatus': False})
        self.assertEqual(self.ep_client.setPublicStatus(pad_id, True), None)
        self.assertEqual(self.ep_client.getPublicStatus(pad_id), {'publicStatus': True})
        self.assertEqual(self.ep_client.setPublicStatus(pad_id, False), None)
        self.assertEqual(self.ep_client.getPublicStatus(pad_id), {'publicStatus': False})

        # Delete group
        self.assertEqual(self.ep_client.deleteGroup(group_id), None)

        # Get and set public status of non-existing pad
        with self.assertRaises(ValueError) as cm:
            self.ep_client.getPublicStatus('Pussycat')
        self.assertEqual(str(cm.exception), 'You can only get/set the publicStatus of pads that belong to a group')
        with self.assertRaises(ValueError) as cm:
            self.ep_client.setPublicStatus('Pussycat', False)
        self.assertEqual(str(cm.exception), 'You can only get/set the publicStatus of pads that belong to a group')

    def testCopy(self):
        pad_id = self.pad_id
        text = self.text
        n_pad_ids = ['Miezhaus', 'Muskelkater', 'Katzenjammer']

        # Create pad, add Text and save Revision
        self.assertEqual(self.ep_client.createPad(pad_id), None)
        self.assertEqual(self.ep_client.listAllPads(), {'padIDs': [pad_id]})
        self.assertEqual(self.ep_client.setText(pad_id, text), None)
        self.assertEqual(self.ep_client.saveRevision(pad_id), None)
        self.assertEqual(self.ep_client.getRevisionsCount(pad_id), {'revisions': 1})
        self.assertEqual(self.ep_client.listSavedRevisions(pad_id), {'savedRevisions': [1]})

        # Copy pad
        self.assertEqual(self.ep_client.copyPad(pad_id, n_pad_ids[0]), None)
        self.assertCountEqual(self.ep_client.listAllPads(), {'padIDs': [pad_id, n_pad_ids[0]]})

        # Copy pad and overwrite existing pad
        self.assertEqual(self.ep_client.createPad(n_pad_ids[1]), None)
        self.assertCountEqual(self.ep_client.listAllPads(), {'padIDs': [pad_id, n_pad_ids[0], n_pad_ids[1]]})
        self.assertEqual(self.ep_client.copyPad(pad_id, n_pad_ids[1], force=True), None)
        self.assertCountEqual(self.ep_client.listAllPads(), {'padIDs': [pad_id, n_pad_ids[0], n_pad_ids[1]]})

        # Copy pad and overwrite non-existing pad
        self.assertEqual(self.ep_client.copyPad(pad_id, n_pad_ids[2], force=True), None)
        self.assertCountEqual(self.ep_client.listAllPads(), {'padIDs': [pad_id, n_pad_ids[0],
                                                                        n_pad_ids[1], n_pad_ids[2]]})

        # Compare new pads against source pad
        for n_pad_id in n_pad_ids:
            self.assertEqual(self.ep_client.getText(pad_id), self.ep_client.getText(n_pad_id))
            self.assertEqual(self.ep_client.getRevisionsCount(pad_id), self.ep_client.getRevisionsCount(n_pad_id))
            self.assertEqual(self.ep_client.listSavedRevisions(pad_id), self.ep_client.listSavedRevisions(n_pad_id))

        # Delete pads
        self.assertEqual(self.ep_client.deletePad(pad_id), None)
        for n_pad_id in n_pad_ids:
            self.assertEqual(self.ep_client.deletePad(n_pad_id), None)

        # Copy non-existing pad
        with self.assertRaises(ValueError) as cm:
            self.ep_client.copyPad(pad_id, n_pad_ids[0])
        self.assertEqual(str(cm.exception), 'padID does not exist')

        with self.assertRaises(ValueError) as cm:
            self.ep_client.copyPad(pad_id, n_pad_ids[0], force=True)
        self.assertEqual(str(cm.exception), 'padID does not exist')

    def testCopyWithoutHistory(self):
        pad_id = self.pad_id
        text = self.text
        n_pad_ids = ['Miezhaus', 'Muskelkater', 'Katzenjammer']

        # Create pad, add Text and save Revision
        self.assertEqual(self.ep_client.createPad(pad_id), None)
        self.assertEqual(self.ep_client.listAllPads(), {'padIDs': [pad_id]})
        self.assertEqual(self.ep_client.getRevisionsCount(pad_id), {'revisions': 0})
        self.assertEqual(self.ep_client.setText(pad_id, text), None)
        self.assertEqual(self.ep_client.saveRevision(pad_id), None)
        self.assertEqual(self.ep_client.getRevisionsCount(pad_id), {'revisions': 1})
        self.assertEqual(self.ep_client.listSavedRevisions(pad_id), {'savedRevisions': [1]})

        # Copy pad
        self.assertEqual(self.ep_client.copyPadWithoutHistory(pad_id, n_pad_ids[0]), None)
        self.assertCountEqual(self.ep_client.listAllPads(), {'padIDs': [pad_id, n_pad_ids[0]]})

        # Copy pad and overwrite existing pad
        self.assertEqual(self.ep_client.createPad(n_pad_ids[1]), None)
        self.assertCountEqual(self.ep_client.listAllPads(), {'padIDs': [pad_id, n_pad_ids[0], n_pad_ids[1]]})
        self.assertEqual(self.ep_client.copyPadWithoutHistory(pad_id, n_pad_ids[1], force=True), None)
        self.assertCountEqual(self.ep_client.listAllPads(), {'padIDs': [pad_id, n_pad_ids[0], n_pad_ids[1]]})

        # Copy pad and overwrite non-existing pad
        self.assertEqual(self.ep_client.copyPadWithoutHistory(pad_id, n_pad_ids[2], force=True), None)
        self.assertCountEqual(self.ep_client.listAllPads(), {'padIDs': [pad_id, n_pad_ids[0],
                                                                        n_pad_ids[1], n_pad_ids[2]]})

        # Compare new pads against source pad
        for n_pad_id in n_pad_ids:
            self.assertEqual(self.ep_client.getText(pad_id)['text'] + "\n", self.ep_client.getText(n_pad_id)['text'])
            # TODO:if the revisions are not saved why aren't the revisioncounter also set back to zero?
            # self.assertEqual(self.ep_client.getRevisionsCount(n_pad_id), {'revisions': 0})
            self.assertEqual(self.ep_client.listSavedRevisions(n_pad_id), {'savedRevisions': []})

        # Delete pads
        self.assertEqual(self.ep_client.deletePad(pad_id), None)
        for n_pad_id in n_pad_ids:
            self.assertEqual(self.ep_client.deletePad(n_pad_id), None)

        # Copy non-existing pad
        with self.assertRaises(ValueError) as cm:
            self.ep_client.copyPadWithoutHistory(pad_id, n_pad_ids[0])
        self.assertEqual(str(cm.exception), 'padID does not exist')

        with self.assertRaises(ValueError) as cm:
            self.ep_client.copyPadWithoutHistory(pad_id, n_pad_ids[0], force=True)
        self.assertEqual(str(cm.exception), 'padID does not exist')

    def testMovePad(self):
        """Create pad and move pad"""
        pad_id = self.pad_id
        text = self.text
        n_pad_ids = ['Miezhaus', 'Muskelkater', 'Katzenjammer']

        # Create pad, add Text and save Revision
        self.assertEqual(self.ep_client.createPad(pad_id), None)
        self.assertEqual(self.ep_client.listAllPads(), {'padIDs': [pad_id]})
        self.assertEqual(self.ep_client.getRevisionsCount(pad_id), {'revisions': 0})
        self.assertEqual(self.ep_client.setText(pad_id, text), None)
        self.assertEqual(self.ep_client.saveRevision(pad_id), None)
        self.assertEqual(self.ep_client.getRevisionsCount(pad_id), {'revisions': 1})
        self.assertEqual(self.ep_client.listSavedRevisions(pad_id), {'savedRevisions': [1]})

        # Move pad
        self.assertEqual(self.ep_client.movePad(pad_id, n_pad_ids[0]), None)
        self.assertCountEqual(self.ep_client.listAllPads(), {'padIDs': [n_pad_ids[0]]})
        self.assertEqual(self.ep_client.getRevisionsCount(n_pad_ids[0]), {'revisions': 1})
        self.assertEqual(self.ep_client.listSavedRevisions(n_pad_ids[0]), {'savedRevisions': [1]})

        # Move pad and overwrite existing pad
        self.assertEqual(self.ep_client.createPad(n_pad_ids[1]), None)
        self.assertCountEqual(self.ep_client.listAllPads(), {'padIDs': [n_pad_ids[0], n_pad_ids[1]]})
        self.assertEqual(self.ep_client.movePad(n_pad_ids[0], n_pad_ids[1], force=True), None)
        self.assertCountEqual(self.ep_client.listAllPads(), {'padIDs': [n_pad_ids[1]]})
        self.assertEqual(self.ep_client.getRevisionsCount(n_pad_ids[1]), {'revisions': 1})
        self.assertEqual(self.ep_client.listSavedRevisions(n_pad_ids[1]), {'savedRevisions': [1]})

        # Move pad and overwrite non-existing pad
        self.assertEqual(self.ep_client.movePad(n_pad_ids[1], pad_id, force=True), None)
        self.assertCountEqual(self.ep_client.listAllPads(), {'padIDs': [pad_id]})
        self.assertEqual(self.ep_client.getRevisionsCount(pad_id), {'revisions': 1})
        self.assertEqual(self.ep_client.listSavedRevisions(pad_id), {'savedRevisions': [1]})

        # Delete pad
        self.assertEqual(self.ep_client.deletePad(pad_id), None)

        # Copy non-existing pad
        with self.assertRaises(ValueError) as cm:
            self.ep_client.copyPadWithoutHistory(pad_id, n_pad_ids[0])
        self.assertEqual(str(cm.exception), 'padID does not exist')

        with self.assertRaises(ValueError) as cm:
            self.ep_client.copyPadWithoutHistory(pad_id, n_pad_ids[0], force=True)
        self.assertEqual(str(cm.exception), 'padID does not exist')

    def testGetLastEdited(self):
        pad_id = self.pad_id

        # Create pad, add text and check timestamp of last edit
        self.assertEqual(self.ep_client.createPad(pad_id), None)
        self.assertEqual(self.ep_client.listAllPads(), {'padIDs': [pad_id]})

        first_edit = self.ep_client.getLastEdited(pad_id)['lastEdited']
        self.ep_client.setText(pad_id, "hello World")
        self.assertGreater(self.ep_client.getLastEdited(pad_id)['lastEdited'], first_edit)

        # Delete pad
        self.assertEqual(self.ep_client.deletePad(pad_id), None)

    def testCheckToken(self):
        # Docu says code 4 "no or wrong API Key" but Etherpad gives HTTP 401.
        # Issue: https://github.com/ether/etherpad-lite/issues/5409
        # Check valid token
        self.assertEqual(self.ep_client.checkToken(), None)

        # # Check invalid token
        ep_client_i = PyEtherpad.EtherpadLiteClient('GuckDieKatzeTanztAlleinTanztUndTanztAufEinemBein', baseUrl)
        # print(ep_client_i.checkToken())
        with self.assertRaises(urllib_error.HTTPError) as cm:
            ep_client_i.checkToken()
        self.assertEqual(str(cm.exception), 'HTTP Error 401: Unauthorized')

    # def padUsersCount(self, padID):

    # def padUsers(self, padID):

    # def getReadOnlyID(self, padID):

    # def getPadID(self, readOnlyID):

    # def listAuthorsOfPad(self, padID):

    # def sendClientsMessage(self, padID, msg):

    # PADS

    def testListAllPads(self):
        """List all pads. Read empty padlist, create pad, check list again and remove pad"""
        random_name = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(10))
        self.assertEqual(self.ep_client.listAllPads(), {'padIDs': []})
        self.ep_client.createPad(random_name)
        self.assertEqual(self.ep_client.listAllPads(), {'padIDs': [random_name]})
        self.ep_client.deletePad(random_name)
        self.assertEqual(self.ep_client.listAllPads(), {'padIDs': []})

    # GLOBAL


if __name__ == "__main__":
    unittest.main(apiKey)
