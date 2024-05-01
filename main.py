import os
import time

import redis.asyncio as redis
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi_limiter import FastAPILimiter
from sqlalchemy import text
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

from src.config import messages
from src.config.config import settings
from src.database.db import get_db
from src.routes import contacts, auth, users

app = FastAPI()

origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix='/api')
app.include_router(contacts.router, prefix="/api")
app.include_router(users.router, prefix='/api')


@app.on_event("startup")
async def startup():
    """
    The startup function is called when the application starts up.
    It can be used to perform tasks that are needed before the application can serve requests, such as initializing a
    database connection or setting up caches.

    :return: A coroutine, which is async
    """
    r = await redis.Redis(host=settings.redis_host, port=settings.redis_port, password=settings.redis_password, db=0,
                          encoding="utf-8",
                          decode_responses=True)
    await FastAPILimiter.init(r)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    The add_process_time_header function adds a 'My-Process-Time' header to the response with the time taken to process the request.

    :param request: Request: Access the incoming request object
    :param call_next: Call the next middleware or route handler
    :return: The response object with the added 'my-process-time' header
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["My-Process-Time"] = str(process_time)
    return response


@app.get("/", name="Project")
def read_root():
    """
    The read_root function is a simple function that returns the message &quot;Hello, world!&quot; in a dictionary.

    :return: A dictionary, so the return_type is dict
    """
    return {"message": "Hello, world!"}


@app.get("/api/healthchecker")
def healthchecker(db: Session = Depends(get_db)):
    """
    The healthchecker function is used to check the health of the API by executing a query on the database.

    :param db: Session: Pass the database session to the function
    :return: A message indicating the health status of the api
    """
    try:
        # Make request
        result = db.execute(text("SELECT 1")).fetchone()
        print(result)
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=messages.DATABASE_ERROR,
            )
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=messages.DATABASE_CONNECTION_ERROR,
        )


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=int(os.environ.get("PORT", 8000)), log_level="info")