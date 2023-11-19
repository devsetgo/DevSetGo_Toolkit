# -*- coding: utf-8 -*-
from .base_schema import SchemaBase
from .database_connector import AsyncDatabase
from .database_ops import DatabaseOperations
from .http_codes import ALL_HTTP_CODES
from .http_codes import DELETE_CODES
from .http_codes import GET_CODES
from .http_codes import PATCH_CODES
from .http_codes import POST_CODES
from .http_codes import PUT_CODES
from .http_codes import common_codes
from .http_codes import generate_code_dict

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
