"""This module contains test class that simulates retrieving exchange rates without actual data requesting."""

from api import _Api


class Api(_Api):
    """The class that simulates data requesting and retrieving from an external data source."""
    def __init__(self):
        # Initialize corresponding logger using the constructor from the base class
        super().__init__("TestApi")

    def _update_rate(self, xrate):
        """The main method of this class-handler. It must return the final rate.

        This method will be called from the update_rate method that is described in the base class _API.

        Args:
            xrate (XRate): the corresponding DB entity.

        Returns:
            float: The pre-defined value of exchange rate.

        """
        rate = 1.01
        return rate
