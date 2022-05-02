# pylint: disable="missing-module-docstring"
import logging
from typing import Dict

from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport

logger = logging.getLogger(__name__)

# pylint: disable="too-few-public-methods"
class MondayDotComClient:
    """
    A wrapper around the graphql client
    """

    def __init__(self, url: str = "https://api.monday.com/v2", monday_key: str = ""):

        headers = {"Authorization": monday_key}

        # Select your transport with a defined url endpoint
        transport = AIOHTTPTransport(url=url, headers=headers)

        # Create a GraphQL client using the defined transport
        self.client = Client(
            transport=transport,
            fetch_schema_from_transport=True,
        )

    def query(self, query: str, variables: Dict = None):
        """
        Hand in query -- as triple quoted string, e.g. -- and
        an optional dictionary of variables.

        Returns the json result if successful
        """

        if not isinstance(variables, dict):
            logger.warning("Query called with improper variable structure.")
            return None

        # Execute the query on the transport
        if variables:
            result = self.client.execute(gql(query), variable_values=variables)
        else:
            result = self.client.execute(gql(query))

        return result
