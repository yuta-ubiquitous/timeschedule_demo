from datetime import datetime

import sqlalchemy as sa
from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from timeschedule import db
from timeschedule.models import Schedule

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
async def read_schedules(
    request: Request, engine: sa.engine.Connectable = Depends(get_engine)
):

    day = datetime.today().strftime("%Y-%m-%d")
    if "date" in request.query_params.keys():
        day = request.query_params["date"]

    schedules = db.find_all(engine)
    context = {"request": request, "schedules": schedules, "day": day}
    return templates.TemplateResponse("index.html", context)


@app.get("/add", response_class=HTMLResponse)
async def add_schedule(request: Request):
    return templates.TemplateResponse("add.html", {"request": request})


@app.post("/add", response_class=HTMLResponse)
async def add_schedule(
    request: Request,
    engine: sa.engine.Connectable = Depends(get_engine),
    name: str = Form(...),
    datetime_start_str: str = Form(...),
    datetime_end_str: str = Form(...),
):

    # 受け取った文字列の日時をdatetime型に変換
    datetime_start = datetime.strptime(datetime_start_str, "%Y-%m-%d %H:%M")
    datetime_end = datetime.strptime(datetime_end_str, "%Y-%m-%d %H:%M")

    # dbに追加
    db.add(
        engine,
        Schedule(name=name, datetime_start=datetime_start, datetime_end=datetime_end),
    )

    return templates.TemplateResponse("add.html", {"request": request})
