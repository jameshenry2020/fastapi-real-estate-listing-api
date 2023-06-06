from fastapi import FastAPI
from . import models
from .database import Base, engine
from .routers import auth, agents

# models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    docs_url="/documentation",
    redoc_url="/redocs",
    title="Real Estate Properties Listing RestAPI",
    description="this is a RestAPI for a Real Estate Properties listing platform where client can search and see properties for rent and sell.",
    version="1.0",
    contact={
        "name": "Agbonlahor Henry",
        "website": "https://henrycodingstack.com",
        "email": "aengrhenry@gmail.com",
    },

)
app.include_router(auth.router)
app.include_router(agents.router)