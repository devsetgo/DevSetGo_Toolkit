# -*- coding: utf-8 -*-
from .base_schema import SchemaBase
from .database_connector import AsyncDatabase
from .database_ops import DatabaseOperations
from .http_codes import (
    ALL_HTTP_CODES,
    DELETE_CODES,
    GET_CODES,
    PATCH_CODES,
    POST_CODES,
    PUT_CODES,
    common_codes,
    generate_code_dict,
)

# import logging

# logger = logging.getLogger('Devsetgo Toolkit')
# logger.setLevel(logging.DEBUG)

# ch = logging.StreamHandler()
# ch.setLevel(logging.DEBUG)

# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# ch.setFormatter(formatter)

# logger.addHandler(ch)

# logger.debug('debug message')
# logger.info('info message')
# logger.warning('warn message')
# logger.error('error message')
# logger.critical('critical message')
