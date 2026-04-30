# -*- coding: utf-8 -*-
import logging

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    # arch and inherit_id are fully handled by the XML data file.
    # Nothing to do here.
    _logger.info("[payment_term_fixed_date] post_init_hook OK (nothing to do)")


def post_migrate(env, version_from=None, version_to=None):
    _logger.info("[payment_term_fixed_date] post_migrate OK (nothing to do)")
