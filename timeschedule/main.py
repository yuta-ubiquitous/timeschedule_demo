import sqlalchemy as sa
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from timeschedule import db

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# DBの設定
database_url: str = "sqlite:///schedule.db"
db_engine = sa.create_engine(database_url, echo=True)
db.create_table(db_engine)


def get_engine() -> sa.engine.Connectable:
    return db_engine


@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/add", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("add.html", {"request": request})


@app.post("/add", response_class=HTMLResponse)
async def add_schedule(
    request: Request,
    name: str = Form(...),
    datetime_start: str = Form(...),
    datetime_end: str = Form(...),
):
    print(name, datetime_start, datetime_end)
    return templates.TemplateResponse("add.html", {"request": request})
