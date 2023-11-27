# -*- coding: utf-8 -*-
# import json
# import logging
# import time

# from email_validator import EmailNotValidError
# from email_validator import validate_email
# from fastapi import APIRouter
# from fastapi import File
# from fastapi import HTTPException
# from fastapi import UploadFile
# from fastapi import status
# from fastapi.responses import ORJSONResponse
# from loguru import logger
# from pydantic import BaseModel
# from pydantic import Field
# from sqlalchemy import inspect
# from sqlalchemy import text
# from src.settings import settings
# from xmltodict import parse as xml_parse
# from xmltodict import unparse as xml_unparse

# # from .database_connector import AsyncDatabase
# from .toolkit import AsyncDatabase

# router = APIRouter()


# # app route /api/v1/tools
# @router.post("/xml-json")
# async def convert_xml(
#     myfile: UploadFile = File(...),
# ) -> dict:
#     """
#     convert xml document to json

#     Returns:
#         json object
#     """

#     # determine if file has no content_type set
#     # set file_type to a value
#     if len(myfile.content_type) == 0:
#         file_type = "unknown"
#     else:
#         file_type = myfile.content_type

#     logger.info(f"file_name: {myfile.filename} file_type: {file_type}")

#     file_named = myfile.filename
#     # if document is not a xml document, give http exception
#     if file_named.endswith(".xml", 4) is not True:
#         error_exception = (
#             f"API requires a XML docuement, but file {myfile.filename} is {file_type}"
#         )
#         logger.error(error_exception)
#         raise HTTPException(status_code=400, detail=error_exception)

#     try:
#         # async method to get data from file upload
#         contents = await myfile.read()
#         # xml to json conversion with xmltodict
#         result = xml_parse(
#             contents, encoding="utf-8", process_namespaces=True, xml_attribs=True
#         )
#         logger.info("file converted to JSON")
#         return result

#     except Exception as e:
#         logger.error(f"error: {e}")
#         err = str(e)
#         # when error occurs output http exception
#         if err.startswith("syntax error") is True or e is not None:
#             error_exception = f"The syntax of the object is not valid. Error: {e}"
#             raise HTTPException(status_code=400, detail=error_exception)


# # app route /api/v1/tools
# @router.post("/json-xml")
# async def convert_json(
#     myfile: UploadFile = File(...),
# ) -> str:
#     """
#     convert json document to xml

#     Returns:
#         XML object
#     """

#     # determine if file is of zero bytes
#     # set file_type to a value
#     if len(myfile.content_type) == 0:
#         file_type = "unknown"
#     else:
#         file_type = myfile.content_type

#     logger.info(f"file_name: {myfile.filename} file_type: {file_type}")

#     file_named = myfile.filename
#     # if document is not a json document, give http exception
#     if file_named.endswith(".json", 5) is not True:
#         error_exception = (
#             f"API requirs a JSON docuement, but file {myfile.filename} is {file_type}"
#         )
#         logger.error(error_exception)
#         raise HTTPException(status_code=400, detail=error_exception)

#     try:
#         # async method to get data from file upload
#         content = await myfile.read()
#         # create a dictionary with decoded content
#         new_dict = json.loads(content.decode("utf8"))
#         # xml to json conversion with xmltodict
#         result = xml_unparse(new_dict, pretty=True)
#         logger.info("file converted to JSON")
#         return result

#     except Exception as e:
#         logger.error(f"error: {e}")
#         err = str(e)
#         # when error occurs output http exception
#         if err.startswith("Extra data") is True or e is not None:
#             error_exception = f"The syntax of the object is not valid. Error: {e}"
#             raise HTTPException(status_code=400, detail=error_exception)


# # app route /api/v1/tools
# @router.get("/database_type/")
# async def database_type():
#     async with AsyncDatabase().get_db_session() as session:
#         try:
#             # Check for PostgreSQL
#             result = await session.execute(text("SELECT version();"))
#             if "PostgreSQL" in result.scalar():
#                 return {"database_type": "PostgreSQL"}

#             # Check for MySQL
#             result = await session.execute(text("SELECT VERSION();"))
#             if "MySQL" in result.scalar():
#                 return {"database_type": "MySQL"}

#             # Check for SQLite
#             result = await session.execute(text("SELECT sqlite_version();"))
#             if (
#                 result.scalars().first() is not None
#             ):  # SQLite will return a version number
#                 return {"database_type": "SQLite"}

#             # Check for Oracle
#             result = await session.execute(
#                 text("SELECT * FROM v$version WHERE banner LIKE 'Oracle%';")
#             )
#             if "Oracle" in result.scalars().first():
#                 return {"database_type": "Oracle"}

#         except Exception as e:
#             return {"error": str(e)}


# # app route /api/v1/tools
# @router.get("/database_dialect/")
# async def database_dialect():
#     async with AsyncDatabase().engine.begin() as conn:
#         dialect = await conn.run_sync(lambda conn: inspect(conn).dialect.name)
#     return {"database_type": dialect}


# # app route /api/v1/tools
# @router.get("/config")
# async def get_config():
#     return settings.dict()


# class EmailVerification(BaseModel):
#     email_address: str = Field(
#         ..., description="The email address to be checked", examples=["test@gmail.com"]
#     )
#     check_deliverability: bool = Field(True, description="Check the dns of the domain")
#     test_environment: bool = Field(
#         False, description="Used for test environments to bypass dns check"
#     )


# @router.post(
#     "/email-validation", response_class=ORJSONResponse, status_code=status.HTTP_200_OK
# )
# async def check_email(
#     # email_address: str = Query(...),
#     # check_deliverability: bool = Query(True),
#     # test_environment: bool = Query(False),
#     email_verification: EmailVerification,
# ):
#     t0 = time.time()
#     try:
#         email_data = await validate_email_address(
#             email_address=email_verification.email_address,
#             check_deliverability=email_verification.check_deliverability,
#             test_environment=email_verification.test_environment,
#         )

#         t1 = time.time() - t0

#         if "error" in email_data:
#             return email_data
#         else:
#             email_data["duration_seconds"] = round(t1, 4)
#             data = email_data

#         logger.debug(f"email validation data: {data} {t1:.4f}")
#         # Log a success message
#         logger.info(
#             f"Email validation succeeded for: {email_verification.email_address}"
#         )

#         return data

#     except Exception as e:
#         t1 = time.time() - t0
#         # Log an error message for other exceptions
#         logger.error(
#             f"Error processing email address: {email_verification.email_address}, error: {str(e)}"
#         )

#         raise HTTPException(status_code=500, detail=str(e))

# async def validate_email_address(
#     email_address: str,
#     check_deliverability: bool = True,
#     test_environment: bool = False,
# ):
#     if not email_address:
#         raise HTTPException(status_code=400, detail="Email address is required")

#     try:
#         email_data = validate_email(
#             email_address,
#             check_deliverability=check_deliverability,
#             test_environment=test_environment,
#         )
#         data = {
#             "normalized": email_data.normalized,
#             "valid": True,
#             "local_part": email_data.local_part,
#             "domain": email_data.domain,
#             "ascii_email": email_data.ascii_email,
#             "ascii_local_part": email_data.ascii_local_part,
#             "ascii_domain": email_data.ascii_domain,
#             "smtputf8": email_data.smtputf8,
#             "mx": None if not check_deliverability else email_data.mx,
#             "mx_fallback_type": None
#             if not check_deliverability
#             else email_data.mx_fallback_type,
#         }
#         return data
#     except EmailUndeliverableError as ex:
#         return {"email_address": email_address, "valid": False, "error": f"EmailUndeliverableError '{str(ex)}'"}

#     except EmailNotValidError as ex:
#         return {"email_address": email_address, "valid": False, "error": f"EmailNotValidError '{str(ex)}'"}

#     except Exception as ex:
#         return {"email_address": email_address, "valid": False, "error": f"An Exception for '{str(ex)}' has occured. This could be due to no value is set on the domain."}
