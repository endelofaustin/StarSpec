from fastapi import FastAPI, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import aiohttp
import asyncio
import logging
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os

# Define the directory for state files
state_dir = "state"
os.makedirs(state_dir, exist_ok=True)  # Ensure the directory exists

class URLModel(BaseModel):
    url: str

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return RedirectResponse(url="/static/index.html")

async def ping_url(url: str):
    logging.info(f"Pinging URL: {url}")
    status = 'red'
    try:
        async with aiohttp.ClientSession() as http_session:
            async with http_session.get(url) as response:
                status = 'green' if response.status == 200 else 'red'
    except Exception as e:
        logging.error(f"Error pinging {url}: {e}")
    append_url_status_to_file(url, status)

def get_state_file_path(url: str, counter: int) -> str:
    filename = url.replace('http://', '').replace('https://', '').replace('/', '_')
    return os.path.join(state_dir, f"{counter}.{filename}.txt")

def append_url_status_to_file(url: str, status: str):
    pattern = url.replace('http://', '').replace('https://', '').replace('/', '_') + '.txt'
    files = sorted([f for f in os.listdir(state_dir) if pattern in f])
    counter = 0
    file_path = get_state_file_path(url, counter)
    if files:
        latest_file = files[-1]
        counter = int(latest_file.split('.')[0])
        file_path = os.path.join(state_dir, latest_file)
        with open(file_path, 'r') as file:
            lines = file.readlines()
        if len(lines) >= 15:
            counter += 1
            file_path = get_state_file_path(url, counter)
            with open(file_path, 'w') as file:
                file.write(f"{status}\n")
        else:
            with open(file_path, 'a') as file:
                file.write(f"{status}\n")
    else:
        with open(file_path, 'w') as file:
            file.write(f"{status}\n")

@app.get("/status/")
async def get_status(url: str):
    history = []
    file_counter = None
    pattern = url.replace('http://', '').replace('https://', '').replace('/', '_') + '.txt'
    for filename in sorted(os.listdir(state_dir)):
        if pattern in filename:
            with open(os.path.join(state_dir, filename), 'r') as file:
                if file_counter is None:
                    file_counter = int(filename.split('.')[0])
                history.extend(file.read().splitlines())
    return {"history": history, "file_counter": file_counter}

@app.post("/add_url")
async def add_url(url_data: URLModel, background_tasks: BackgroundTasks):
    url = url_data.url.strip()
    if not url.startswith(('http://', 'https://')):
        return {"status": "error", "message": "Invalid URL"}
    background_tasks.add_task(ping_url, url)
    return {"status": "success", "url": url}

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(monitor_urls())

async def monitor_urls():
    logging.info("Monitoring URLs started.")
    while True:
        try:
            for filename in sorted(os.listdir(state_dir)):
                if '.' in filename:
                    counter, safe_url = filename.split('.', 1)
                    url = "http://" + safe_url.rsplit('.', 1)[0].replace('_', '/')
                    logging.info(f"Scheduled pinging for: {url}")
                    await ping_url(url)
        except Exception as e:
            logging.error(f"Error in monitor_urls: {str(e)}")
        await asyncio.sleep(60)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    uvicorn.run(app, host="127.0.0.1", port=8000)
