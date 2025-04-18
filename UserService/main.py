from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import UserController

app = FastAPI()
app.include_router(UserController.router)

origins = [
    "http://localhost:80",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the startup method
@app.on_event("startup")
async def startup_event():
    # Call your method(s) to create tables or perform any startup tasks
    print("Running startup tasks...")
    print("Start up tasks completed")
    