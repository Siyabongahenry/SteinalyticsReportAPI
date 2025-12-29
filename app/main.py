from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.routers import vip_validation
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow requests from specific origins (frontend URLs)
origins = [
    "http://localhost:5173",   # React dev
    "https://steinalytics.takemali.com"   # Production frontend
    "https://steinalytics.com"   # Production frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # List of allowed origins
    allow_credentials=True,
    allow_methods=["*"],            # GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],            # Allow all headers
)
#incorrect vip codes validation router
app.include_router(vip_validation.router)

@app.get("/")
def read_root():
    return {"message":"Welcome to Steinalytics API"}