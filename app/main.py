from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.settings import settings
from fastapi.responses import JSONResponse
from app.utils.exceptions import AuthorizationError


#routers import
from app.api.v1.routers import (
    vip_validation_router,
    overbooking_identify_router,
    lookup_router,
    multiple_clockings_router,
    exemption_router,
    devices_router,
    attendance_router
)


app = FastAPI()

# Allow requests from specific origins (frontend URLs)

origins = [origin.strip() for origin in settings.core_origins.split(",") if origin.strip()]

print(origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # List of allowed origins
    allow_credentials=True,
    allow_methods=["*"],            # GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],            # Allow all headers
)

app.include_router(vip_validation_router.router)
app.include_router(overbooking_identify_router.router)
app.include_router(lookup_router.router)
app.include_router(multiple_clockings_router.router)
app.include_router(exemption_router.router)
app.include_router(devices_router.router)
app.include_router(attendance_router.router)

@app.exception_handler(AuthorizationError)
def authz_exception_handler(_, __):
    return JSONResponse(
        status_code=403,
        content={"detail": "Forbidden"},
    )

@app.get("/")
def read_root():
    return {"message":"Welcome to Steinalytics API"}
