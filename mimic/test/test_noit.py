import uuid
import xmltodict
import json
from twisted.trial.unittest import SynchronousTestCase
from twisted.internet.task import Clock

from mimic.core import MimicCore
from mimic.resource import MimicRoot
from mimic.test.helpers import request_with_content


class NoitAPITests(SynchronousTestCase):

    """
    Tests for noit API plugin
    """

    def setUp(self):
        """
        Create a check
        """
        core = MimicCore(Clock(), [])
        self.root = MimicRoot(core).app.resource()
        self.create_check = {
            "check": {
                "attributes": {
                    "name": "name",
                    "module": "module",
                    "target": "target",
                    "period": "period",
                    "timeout": "timeout",
                    "filterset": "filterset"
                }
            }}
        self.create_check_xml_payload = xmltodict.unparse(self.create_check
                                                          ).encode("utf-8")
        self.check_id = uuid.uuid4()
        url = "noit/checks/set/{0}".format(self.check_id)

        (self.response, self.body) = self.successResultOf(
            request_with_content(self, self.root, "PUT", url,
                                 body=self.create_check_xml_payload))

    def test_get_all_checks(self):
        """
        Test to verify :func:`get_all_checks` on ``GET /config/checks``
        """
        (response, body) = self.successResultOf(
            request_with_content(self, self.root, "GET", "noit/config/checks"))
        self.assertEqual(response.code, 200)
        json_response = json.loads(json.dumps(xmltodict.parse(body)))
        self.assertGreater(len(json_response["checks"]["check"]), 0)

    def test_test_check(self):
        """
        Test to verify :func:`test_check` on ``POST /checks/test``
        """
        (response, body) = self.successResultOf(
            request_with_content(self, self.root, "POST", "noit/checks/test",
                                 body=self.create_check_xml_payload))
        self.assertEqual(response.code, 200)

    def test_create_check(self):
        """
        Test to verify :func:`set_check` on ``PUT /checks/set/<check_id>``
        """
        self.assertEqual(self.response.code, 200)

    def test_update_check(self):
        """
        Test to verify update check on :func:`set_check` using
        ``PUT /checks/set/<check_id>``
        """
        self.create_check["check"]["attributes"]["names"] = "rename"
        (response, body) = self.successResultOf(
            request_with_content(self, self.root, "PUT",
                                 "noit/checks/set/{0}".format(self.check_id),
                                 body=xmltodict.unparse(self.create_check
                                                        ).encode("utf-8")))
        self.assertEqual(self.response.code, 200)

    def test_get_check(self):
        """
        Test to verify :func:`get_checks` on ``GET /checks/show/<check_id>``
        """
        (get_response, body) = self.successResultOf(
            request_with_content(self, self.root, "GET",
                                 "noit/checks/show/{0}".format(self.check_id)))
        self.assertEqual(get_response.code, 200)

    def test_delete_check(self):
        """
        Test to verify :func:`delete_checks` on
        ``DELETE /checks/delete/<check_id>``
        """
        (del_response, body) = self.successResultOf(
            request_with_content(self, self.root, "DELETE",
                                 "noit/checks/delete/{0}".format(self.check_id)))
        self.assertEqual(del_response.code, 200)

    def test_create_check_fails_with_500(self):
        """
        Test to verify :func:`set_check` results in error 500,
        when the xml cannot be parsed.
        """
        (response, body) = self.successResultOf(
            request_with_content(self, self.root, "PUT",
                                 "noit/checks/set/{0}".format(self.check_id),
                                 body=self.create_check_xml_payload.replace(
                                     '</check>', ' abc')))
        self.assertEqual(response.code, 500)

    def test_create_check_fails_with_500_for_invalid_check_id(self):
        """
        Test to verify :func:`set_check` results in error 500,
        when the xml cannot be parsed.
        """
        (response, body) = self.successResultOf(
            request_with_content(self, self.root, "PUT",
                                 "noit/checks/set/123444",
                                 body=self.create_check_xml_payload))
        self.assertEqual(response.code, 500)
