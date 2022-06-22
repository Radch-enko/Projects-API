from fastapi import FastAPI
from src.routers import discussions, discussionsTopics, projects, reports, users, topics, medias
from src.db.database import engine
from src.db import models
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title = "Projects API")

app.include_router(projects.router)
app.include_router(topics.router)
app.include_router(discussionsTopics.router)
app.include_router(medias.router)
app.include_router(users.router)
app.include_router(discussions.router)
app.include_router(reports.router)

models.Base.metadata.create_all(bind=engine)
app.add_middleware(CORSMiddleware, allow_origins=["*"])
