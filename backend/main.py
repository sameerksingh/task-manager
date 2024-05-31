from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from views import task_views, user_views
import uvicorn

app = FastAPI()

# Allow requests from all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(task_views.router)
app.include_router(user_views.router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)