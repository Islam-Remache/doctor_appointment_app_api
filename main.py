from fastapi import FastAPI, Request, Response
import time
import os
import json
from datetime import datetime
from fastapi import FastAPI
from api import prescription
app = FastAPI()

app.include_router(prescription.router)
