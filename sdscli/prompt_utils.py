from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import print_function

import os, re

from prompt_toolkit.validation import Validator, ValidationError

from sdscli.log_utils import logger


class YesNoValidator(Validator):
    def validate(self, document):
        text = document.text.lower()
        if not text in ('yes', 'no', 'y', 'n'):
            raise ValidationError(message='Input needs to be "y" or "n"',
                                  cursor_position=len(text))


class IpAddressValidator(Validator):
    def validate(self, document):
        match = re.search(r'^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$')
        if not match:
            raise ValidationError(message='Input needs to be valid IP address',
                                  cursor_position=len(text))


def set_bar_desc(bar, message):
    """Set bar description."""

    bar.set_description("{0: >20.20}".format(message))
