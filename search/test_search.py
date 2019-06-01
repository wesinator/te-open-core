"""Testing functions for total email's search capability."""

import html

from django.test import TestCase

from .search_mappings import header_search_mappings
from test_resources import DefaultTestObject

EXPECTED_SEARCH_RESULTS = {"sub": "python", "to": "bob <bob@gmail.com>", "from": "Alice Underwood <alice@gmail.com>"}

EXPECTED_SEARCH_RESULTS_2 = {"sub": "pyth", "to": "bob@gmail.com", "from": "alice@gmail.com"}

EXPECTED_SEARCH_RESULTS_3 = {"sub": "pyth", "to": "bob", "from": "Underwood"}

SEARCH_FUNCTION_TO_DB_MAPPINGS = header_search_mappings
TestData = DefaultTestObject()


class SearchViewTests(TestCase):
    """Search tests."""

    def test_index_view(self):
        """Test the index view."""
        response = self.client.get('/search')
        self.assertContains(response, "Search the Emails")

    def test_empty_basic_search(self):
        TestData.create_email()
        response = self.client.get("/search?q=microsoft")
        assert "Emails matching" not in str(response.content)
        assert 'No results found for "<i>microsoft</i>"' in str(response.content)

    def test_basic_search(self):
        TestData.create_email()
        response = self.client.get("/search?q=github")
        assert 'Found 1 email matching "<i>github</i>"' in str(response.content)
        assert 'No results' not in str(response.content)

    def test_empty_search_function(self):
        """Test a search query without any emails."""
        TestData.create_email()
        response = self.client.get('/search?q=to(microsoft)')
        assert 'No results found for "<i>to(microsoft)</i>"' in str(response.content)

    def test_error_message_on_short_queries(self):
        TestData.create_email()

        # test 1 character
        url = '/search?q=a'
        response = self.client.get(url)
        assert 'Please enter a search term that is 3 characters or longer' in str(response.content)

        # test 2 characters
        url = '/search?q=ab'
        response = self.client.get(url)
        assert 'Please enter a search term that is 3 characters or longer' in str(response.content)

        # test 3 characters
        url = '/search?q=abc'
        response = self.client.get(url)
        assert 'Please enter a search term that is 3 characters or longer' not in str(response.content)

    def test_search_function(self):
        """Test a search query with an email which it should match."""
        TestData.create_email()

        # test each available search function
        for function in SEARCH_FUNCTION_TO_DB_MAPPINGS:
            url = '/search?q={}({})'.format(function, EXPECTED_SEARCH_RESULTS.get(function))
            response = self.client.get(url)

            desired_string = 'Found 1 email matching "<i>{}({})</i>"'.format(
                function, html.escape(EXPECTED_SEARCH_RESULTS.get(function))
            )
            print("response content {}".format(response.content))
            assert desired_string in str(response.content)

    def test_search_function_casing(self):
        """Make sure the case of a search query doesn't cause the user to miss results."""
        TestData.create_email()

        # test each available search function
        for function in SEARCH_FUNCTION_TO_DB_MAPPINGS:
            url = '/search?q={}({})'.format(function, EXPECTED_SEARCH_RESULTS.get(function).title())
            response = self.client.get(url)

            desired_string = 'Found 1 email matching "<i>{}({})</i>"'.format(
                function, html.escape(EXPECTED_SEARCH_RESULTS.get(function).title())
            )
            print("response content {}".format(response.content))
            assert desired_string in str(response.content)

    def test_loose_search_function_1(self):
        """Test a search query with an email which it should match."""
        TestData.create_email()

        # test each available search function
        for function in SEARCH_FUNCTION_TO_DB_MAPPINGS:
            url = '/search?q={}({})'.format(function, EXPECTED_SEARCH_RESULTS_2.get(function))
            response = self.client.get(url)

            desired_string = 'Found 1 email matching "<i>{}({})</i>"'.format(function, EXPECTED_SEARCH_RESULTS_2.get(function))
            print("response content {}".format(response.content))
            assert desired_string in str(response.content)

    def test_loose_search_function_2(self):
        """Test a search query with an email which it should match."""
        TestData.create_email()

        # test each available search function
        for function in SEARCH_FUNCTION_TO_DB_MAPPINGS:
            url = '/search?q={}({})'.format(function, EXPECTED_SEARCH_RESULTS_3.get(function))
            response = self.client.get(url)

            desired_string = 'Found 1 email matching "<i>{}({})</i>"'.format(function, EXPECTED_SEARCH_RESULTS_3.get(function))
            assert desired_string in str(response.content)

    def test_search_with_spaces(self):
        # create two emails
        TestData.create_email()
        TestData.create_email(TestData.attachment_email_text)

        url = '/search?q=python+project+template'
        response = self.client.get(url)
        assert 'Found 1 email matching "<i>python project template</i>"' in str(response.content)

    def test_search_function_bod(self):
        TestData.create_email()

        url = '/search?q=bod(github)'
        response = self.client.get(url)
        print('response {}'.format(str(response.content)))
        assert 'Found 1 email matching "<i>bod(github)</i>"' in str(response.content)

    def test_search_function_dom(self):
        TestData.create_email()

        url = '/search?q=dom(github.com)'
        response = self.client.get(url)
        print('response {}'.format(str(response.content)))
        assert 'Found 1 email matching "<i>dom(github.com)</i>"' in str(response.content)

    def test_search_function_domh(self):
        TestData.create_email()

        url = '/search?q=domh(gmail.com)'
        response = self.client.get(url)
        print('response {}'.format(str(response.content)))
        assert 'Found 1 email matching "<i>domh(gmail.com)</i>"' in str(response.content)

    def test_search_function_domb(self):
        TestData.create_email()

        url = '/search?q=domb(github.com)'
        response = self.client.get(url)
        print('response {}'.format(str(response.content)))
        assert 'Found 1 email matching "<i>domb(github.com)</i>"' in str(response.content)
