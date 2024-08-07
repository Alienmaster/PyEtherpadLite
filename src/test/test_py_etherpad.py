# !/usr/bin/env python
"""Module to test py_etherpad."""

import py_etherpad
import unittest
import random
import string

apiKey = "ef4d13df379edf92f2d2011add171980e59092830a89b62c66a55b914f72dceb"
baseUrl = "http://localhost:9001/api"

class TestEtherpadLiteClient(unittest.TestCase):
    """Class to test EtherpadLiteClient."""

    def setUp(self):
        """Assign a shared EtherpadLiteClient instance to self."""
        self.ep_client = py_etherpad.EtherpadLiteClient(apiKey, baseUrl)

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
            self.assertEqual(self.ep_client.deleteGroup(group))
        self.assertEqual(cm.exception, 'groupID does not exist')

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
        pad_name_one = "Hairball"
        pad_name_two = "Paws"
        standard_content = (
            "Welcome to Etherpad!\n\nThis pad text is synchronized as you type, so that everyone "
            "viewing this page sees the same text. This allows you to collaborate seamlessly on "
            "documents!\n\nGet involved with Etherpad at https://etherpad.org\n\nWarning: DirtyDB is "
            "used. This is not recommended for production. -- To suppress these warning messages "
            "change suppressErrorsInPadText to true in your settings.json\n\n"
        )

        pad_content_two = "Wo lebt eine Katze? Im Miezhaus"

        # Create groups
        before = self.ep_client.listAllGroups()["groupIDs"]

        group_one = self.ep_client.createGroup()["groupID"]
        group_two = self.ep_client.createGroup()["groupID"]
        after = self.ep_client.listAllGroups()["groupIDs"]
        self.assertEqual(len(after), len(before) + 2)

        # Create empty group Pad for group one and list group Pads
        # TODO: Mismatch between Doc and API? Return not Null of "createGroupPad" PR running
        pad_id_one = group_one + "$" + pad_name_one
        self.assertEqual(
            self.ep_client.createGroupPad(group_one, pad_name_one),
            {"padID": pad_id_one},
        )
        self.assertEqual(self.ep_client.listPads(group_one), {"padIDs": [pad_id_one]})
        self.assertEqual(self.ep_client.listPads(group_two), {"padIDs": []})

        # Create prefilled Pad for group two and list group Pads
        pad_id_two = group_two + "$" + pad_name_two
        self.assertEqual(
            self.ep_client.createGroupPad(group_two, pad_name_two, pad_content_two),
            {"padID": pad_id_two},
        )
        # Check if both groups have one pad each
        self.assertEqual(self.ep_client.listPads(group_one), {"padIDs": [pad_id_one]})
        self.assertEqual(self.ep_client.listPads(group_two), {"padIDs": [pad_id_two]})

        # Create the same pad another time
        # TODO PR Running pad =/= padName
        with self.assertRaises(ValueError) as cm:
            self.ep_client.createGroupPad(group_one, pad_name_one)
        self.assertEqual(str(cm.exception), "padName does already exist")

        # Read both group Pads
        self.assertEqual(self.ep_client.getText(pad_id_one), {"text": standard_content})
        text = self.ep_client.getText(pad_id_two)
        self.assertEqual(text, {"text": pad_content_two + "\n"})

        # Delete Pads
        self.assertEqual(self.ep_client.deletePad(pad_id_one), None)
        self.assertEqual(self.ep_client.listPads(group_one), {"padIDs": []})
        self.assertEqual(self.ep_client.listPads(group_two), {"padIDs": [pad_id_two]})
        self.assertEqual(self.ep_client.deletePad(pad_id_two), None)
        self.assertEqual(self.ep_client.listPads(group_two), {"padIDs": []})

        # Delete groups
        self.assertEqual(self.ep_client.deleteGroup(group_one), None)
        self.assertEqual(self.ep_client.deleteGroup(group_two), None)
        end = self.ep_client.listAllGroups()["groupIDs"]
        self.assertEqual(len(end), len(before))

        # Create Pad for non-existing group
        with self.assertRaises(ValueError) as cm:
            self.ep_client.createGroupPad(group_one, pad_name_one)
        self.assertEqual(str(cm.exception), "groupID does not exist")

    # AUTHORS

    def testCreateAuthor(self):
        # TODO missing Test of listOfPadsOfAuthor when Authors has a Pad
        # TODO Doku wrong: getAuthorName returns String of authorName not Dict
        # Create an author
        random_name_one = "".join(
            random.SystemRandom().choice(string.ascii_letters + string.digits)
            for _ in range(10)
        )
        random_name_two = "".join(
            random.SystemRandom().choice(string.ascii_letters + string.digits)
            for _ in range(10)
        )

        author_id_one = self.ep_client.createAuthor(random_name_one)

        # get author name
        self.assertEqual(
            self.ep_client.getAuthorName(author_id_one["authorID"]), random_name_one
        )

        # Create another with authormapper with empty name and check name of both authors
        author_id_two = self.ep_client.createAuthorIfNotExistsFor("")
        self.assertEqual(self.ep_client.getAuthorName(author_id_two["authorID"]), None)
        self.assertEqual(
            self.ep_client.getAuthorName(author_id_one["authorID"]), random_name_one
        )

        # Try to create the first author again with authormapper
        self.assertNotEqual(
            self.ep_client.createAuthorIfNotExistsFor(random_name_one),
            {"authorID": author_id_one["authorID"]},
        )

        # Check first authors pads and create one
        self.assertEqual(
            self.ep_client.listPadsOfAuthor(author_id_one["authorID"]), {"padIDs": []}
        )

        # Check pads of non-existing author
        with self.assertRaises(ValueError) as cm:
            self.assertEqual(self.ep_client.listPadsOfAuthor(random_name_two))
        self.assertEqual(str(cm.exception), "authorID does not exist")

    # SESSIONS

    # PAD CONTENT
    def testPadContent(self):
        text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
        text2 = "new text"
        pad_name_one = "Hairball"
        # setText AuthorID
        # appendText AuthorID
        # setHTML AuthorID
        # getAttributePool
        # getRevisionChangeset Rev
        # createDiffHTML
        # restoreRevision AuthorID

        # Create group and pad
        group_one = self.ep_client.createGroup()["groupID"]
        pad_id_one = group_one + "$" + pad_name_one
        pad_id_one_return = self.ep_client.createGroupPad(group_one, pad_name_one)
        self.assertEqual(pad_id_one_return, {"padID": pad_id_one})

        # Set text and overwrite it # TODO AuthorID
        self.assertEqual(self.ep_client.setText(pad_id_one, text), None)
        self.ep_client.setText(pad_id_one, text2)

        # Get two text revisions and compare
        getText = self.ep_client.getText(pad_id_one)["text"]
        getTextRev1 = self.ep_client.getText(pad_id_one, 1)["text"]
        self.assertEqual(getText, text2 + "\n")
        self.assertEqual(getTextRev1, text + "\n")

        # Append text # TODO AuthorID
        self.assertEqual(self.ep_client.appendText(pad_id_one, text), None)
        getAppendedText = self.ep_client.getText(pad_id_one)["text"]
        self.assertEqual(getAppendedText, text2 + text + "\n")

        # Get and Set HTML text # TODO AuthorID
        html_pre = "<!DOCTYPE HTML><html><body>"
        html_post = "<br></body></html>"
        getHtmlText = self.ep_client.getHtml(pad_id_one)["html"]
        self.assertEqual(getHtmlText, html_pre + text2 + text + html_post)
        br = "<br>"
        self.assertEqual(self.ep_client.setHtml(pad_id_one, br + text + br), None)
        getNewHtmlText = self.ep_client.getHtml(pad_id_one)["html"]
        self.assertEqual(getNewHtmlText, html_pre + br + text + br + html_post)
        getNewHtmlTextRev1 = self.ep_client.getHtml(pad_id_one, 1)["html"]
        self.assertEqual(getNewHtmlTextRev1, html_pre + text + html_post)

        # Restore revision # TODO AuthorID
        self.assertEqual(self.ep_client.restoreRevision(pad_id_one, 1), None)
        getTextResRev1 = self.ep_client.getText(pad_id_one)["text"]
        self.assertEqual(getTextResRev1, getTextRev1+"\n")

    # CHAT

    # PAD

    # PADS

    def testListAllPads(self):
        """List all pads. Read empty padlist, create pad, check list again and remove pad"""
        random_name = "".join(
            random.SystemRandom().choice(string.ascii_letters + string.digits)
            for _ in range(10)
        )
        self.ep_client.createPad(random_name)
        self.assertEqual(self.ep_client.listAllPads(), {'padIDs': [random_name]})
        self.ep_client.deletePad(random_name)
        self.assertEqual(self.ep_client.listAllPads(), {'padIDs': []})

    # GLOBAL


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testCreateLargePad']
    unittest.main(apiKey)
