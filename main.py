# main.py
from fastapi import FastAPI
from api.routes import appointment_routes, notification_routes
from db.session import Base, engine
from db.models import appointment_models

appointment_models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Doctor Appointment API",
    description="API for managing doctor appointments.",
    version="0.1.0"
)

# To match Android's current request of "/appointments/patient/{patient_id}/details"
app.include_router(appointment_routes.router)
app.include_router(notification_routes.router) # Router's own "/appointments" prefix will be used.

@app.get("/")
async def root():
    return {"message": "Welcome to the Doctor Appointment API! Visit /docs for API documentation."}