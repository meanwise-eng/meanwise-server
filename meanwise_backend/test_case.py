import unittest
import uuid
from django.test import LiveServerTestCase
from gabbi import case, suitemaker
from gabbi.driver import test_suite_from_yaml
from gabbi.handlers import RESPONSE_HANDLERS
from gabbi.reporter import ConciseTestRunner
from meanwise_backend import wsgi
from hypothesis.extra.django import TestCase
from six import StringIO


class GabbiHypothesisTestCase(TestCase, LiveServerTestCase):
    """
    Test case to handle running gabbi tests along with hypothesis in django applications.
    """
    def run_gabi(self, gabbi_declaration):
        # initialise the gabbi handlers
        handlers = []
        for handler in RESPONSE_HANDLERS:
            handlers.append(handler())

        # take only the host name and port from the live server
        _, host = self.live_server_url.split('://')
        host, port = host.split(':')

        # use gabbi to create the test suite from our declaration
        suite = suitemaker.test_suite_from_dict(
            unittest.defaultTestLoader,
            self.id(),
            gabbi_declaration,
            '.',
            host,
            port,
            None,
            None,
            handlers=handlers
        )

        # run the test (we store the the output into a custom stream so that hypothesis can display only the simple
        # case test result on failure rather than every failing case)
        s = StringIO()
        result = ConciseTestRunner(stream=s, verbosity=0).run(suite)

        # if we weren't successfull we need to fail the test case with the error string from gabbi
        if not result.wasSuccessful():
            self.fail(s.getvalue())
