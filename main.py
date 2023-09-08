
from fastapi import FastAPI
from database import engine, Base
from routers import contact

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(contact.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
