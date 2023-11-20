# -*- coding: utf-8 -*-
"""
This module provides a health endpoint for the application. It includes the following routes:

- `/api/health/status`: Returns the status of the application. If the application is running, it will return `{"status": "UP"}`.

- `/api/health/uptime`: Returns the uptime of the application in a dictionary with the keys "Days", "Hours", "Minutes", and "Seconds". The uptime is calculated from the time the application was started.

- `/api/health/heapdump`: Returns a heap dump of the application. The heap dump is a list of dictionaries, each representing a line of code. Each dictionary includes the filename, line number, size of memory consumed, and the number of times the line is referenced.

Usage:

```python
from FastAPI import FastAPI
from devsetgo_toolkit import system_health_endpoints

app = FastAPI()
# Health router
app.include_router(system_health_endpoints.router, prefix="/api/health", tags=["system-health"])

```
"""

# Import necessary modules
import time
import tracemalloc

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import ORJSONResponse

from devsetgo_toolkit import generate_code_dict

# Importing database connector module
from devsetgo_toolkit.logger import logger

# Create a new router
router = APIRouter()

# Store the start time of the application
app_start_time = time.time()

# TODO: Create method to enable/disable endpoints from main application.
# TODO: determine method to shutdown/restart python application

status_response = generate_code_dict([400, 405, 500], description_only=False)


def create_health_router(enable_health_endpoints: bool):
    router = APIRouter()

    if enable_health_endpoints:

        @router.get(
            "/status",
            tags=["system-health"],
            status_code=status.HTTP_200_OK,
            response_class=ORJSONResponse,
            responses=status_response,
        )
        async def health_status():
            """
            GET status, uptime, and current datetime

            Returns:
                dict -- [status: UP, uptime: seconds current_datetime: datetime.now]
            """
            logger.info("Health status of up returned")
            # Return a dictionary with the status of the application
            return {"status": "UP"}

        @router.get("/uptime", response_class=ORJSONResponse, responses=status_response)
        async def get_uptime():
            """
            Calculate and return the uptime of the application.

            This function calculates the uptime of the application in days, hours, minutes, and seconds.
            The uptime is calculated as the difference between the current time and the time when the application started.
            The result is returned as a dictionary with the keys 'Days', 'Hours', 'Minutes', and 'Seconds'.

            Raises:
                HTTPException: If any error occurs during the calculation of the uptime, an HTTPException with status code 500 is raised.

            Returns:
                dict: A dictionary with the keys 'Days', 'Hours', 'Minutes', and 'Seconds' and the corresponding uptime values as the values.
            """
            try:
                # Calculate the total uptime in seconds
                uptime_seconds = time.time() - app_start_time
                # Convert the uptime to days, hours, minutes, and seconds
                days, rem = divmod(uptime_seconds, 86400)
                hours, rem = divmod(rem, 3600)
                minutes, seconds = divmod(rem, 60)
                # Log the uptime
                logger.info(
                    f"Uptime: {int(days)} days, {int(hours)} hours, {int(minutes)} minutes, {round(seconds, 2)} seconds"
                )
                # Return a dictionary with the uptime
                return {
                    "uptime": {
                        "Days": int(days),
                        "Hours": int(hours),
                        "Minutes": int(minutes),
                        "Seconds": round(seconds, 2),
                    }
                }
            except Exception as ex:
                logger.error(f"Error in get_uptime: {ex}")
                raise HTTPException(
                    status_code=500, detail=f"Error in get_uptime: {ex}"
                )

        @router.get(
            "/heapdump", response_class=ORJSONResponse, responses=status_response
        )
        async def get_heapdump():
            """
            Add the following to use heapdump:

            import tracemalloc to main FastAPI file

            To the fastAPI start up
            tracemalloc.start()

            To the fastAPI shutdown
            tracemalloc.stop()
            """

            try:
                tracemalloc.start()  # Start tracing memory allocations
                # Take a snapshot of the current memory usage
                snapshot = tracemalloc.take_snapshot()
                # Get the top 10 lines consuming memory
                top_stats = snapshot.statistics("traceback")

                heap_dump = []
                for stat in top_stats[:10]:
                    # Get the first frame from the traceback
                    frame = stat.traceback[0]
                    # Add the frame to the heap dump
                    heap_dump.append(
                        {
                            "filename": frame.filename,
                            "lineno": frame.lineno,
                            "size": stat.size,
                            "count": stat.count,
                        }
                    )

                logger.debug(f"Heap dump returned {heap_dump}")
                # Return the heap dump
                tracemalloc.stop()  # Stop tracing memory allocations
                return {"heap_dump": heap_dump}
            except Exception as ex:
                logger.error(f"Error in get_heapdump: {ex}")
                raise HTTPException(
                    status_code=500, detail=f"Error in get_heapdump: {ex}"
                )

    return router


# # Define a new route for getting the status of the application
# @router.get(
#     "/status",
#     tags=["system-health"],
#     status_code=status.HTTP_200_OK,
#     response_class=ORJSONResponse,
#     responses=status_response,
# )
# async def health_status() -> dict:
#     """
#     GET status, uptime, and current datetime

#     Returns:
#         dict -- [status: UP, uptime: seconds current_datetime: datetime.now]
#     """
#     logger.info("Health status of up returned")
#     # Return a dictionary with the status of the application
#     return {"status": "UP"}


# Define a new route for getting the uptime of the application
# @router.get("/uptime", response_class=ORJSONResponse, responses=status_response)
# async def get_uptime():
#     try:
#         # Calculate the total uptime in seconds
#         uptime_seconds = time.time() - app_start_time
#         # Convert the uptime to days, hours, minutes, and seconds
#         days, rem = divmod(uptime_seconds, 86400)
#         hours, rem = divmod(rem, 3600)
#         minutes, seconds = divmod(rem, 60)
#         # Return a dictionary with the uptime
#         return {
#             "uptime": {
#                 "Days": int(days),
#                 "Hours": int(hours),
#                 "Minutes": int(minutes),
#                 "Seconds": round(seconds, 2),
#             }
#         }
#     except Exception as ex:
#         logger.error(f"Error in get_uptime: {ex}")
#         raise HTTPException(status_code=500, detail=f"Error in get_uptime: {ex}")


# # Define a new route for getting a heap dump of the application
# @router.get("/heapdump", response_class=ORJSONResponse, responses=status_response)
# async def get_heapdump():
#     """
#     Add the following to use heapdump:

#     import tracemalloc to main FastAPI file

#     To the fastAPI start up
#     tracemalloc.start()

#     To the fastAPI shutdown
#     tracemalloc.stop()
#     """

#     try:
#         tracemalloc.start()  # Start tracing memory allocations
#         # Take a snapshot of the current memory usage
#         snapshot = tracemalloc.take_snapshot()
#         # Get the top 10 lines consuming memory
#         top_stats = snapshot.statistics("traceback")

#         heap_dump = []
#         for stat in top_stats[:10]:
#             # Get the first frame from the traceback
#             frame = stat.traceback[0]
#             # Add the frame to the heap dump
#             heap_dump.append(
#                 {
#                     "filename": frame.filename,
#                     "lineno": frame.lineno,
#                     "size": stat.size,
#                     "count": stat.count,
#                 }
#             )

#         logger.debug(f"Heap dump returned {heap_dump}")
#         # Return the heap dump
#         tracemalloc.stop()  # Stop tracing memory allocations
#         return {"heap_dump": heap_dump}
#     except Exception as ex:
#         logger.error(f"Error in get_heapdump: {ex}")
#         raise HTTPException(status_code=500, detail=f"Error in get_heapdump: {ex}")
