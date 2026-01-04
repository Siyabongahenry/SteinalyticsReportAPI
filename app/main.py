from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
#routerss import
from app.api.v1.routers import vip_validation_router
from app.api.v1.routers import overbooking_identify_router
from app.api.v1.routers import lookup_router

app = FastAPI()

# Allow requests from specific origins (frontend URLs)
origins = [
    "http://localhost:5173",   # React dev
    "https://steinalytics.co.za"   # Production frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # List of allowed origins
    allow_credentials=True,
    allow_methods=["*"],            # GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],            # Allow all headers
)
#incorrect vip codes validation router
app.include_router(vip_validation_router.router)
app.include_router(overbooking_identify_router.router)
app.include_router(lookup_router.router)

@app.get("/")
def read_root():
    return {"message":"Welcome to Steinalytics API"}