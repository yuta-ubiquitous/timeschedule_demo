from datetime import datetime, timedelta

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
    """スケジュールの表示をするページ"""

    day = datetime.today().strftime("%Y-%m-%d")
    if "date" in request.query_params.keys():
        day = request.query_params["date"]

    day_datetime = datetime.strptime(day, "%Y-%m-%d")

    schedules = db.find_all(engine)

    # 指定の日付のデータを抽出
    searched_schedules = [
        schedule
        for schedule in schedules
        if not schedule.datetime_end < day_datetime
        and not schedule.datetime_start > (day_datetime + timedelta(days=1))
    ]

    day_jp_format = datetime.strftime(day_datetime, "%Y年%m月%d日")

    context = {
        "request": request,
        "schedules": searched_schedules,
        "day": day,
        "day_str": day_jp_format,
    }
    return templates.TemplateResponse("index.html", context)


@app.get("/add", response_class=HTMLResponse)
async def add_schedule(request: Request):
    """スケジュールを追加するページ（初期状態）"""
    return templates.TemplateResponse("add.html", {"request": request})


@app.post("/add", response_class=HTMLResponse)
async def add_schedule(
    request: Request,
    engine: sa.engine.Connectable = Depends(get_engine),
    name: str = Form(""),
    datetime_start_str: str = Form(""),
    datetime_end_str: str = Form(""),
):
    """スケジュールを追加するページ（追加の処理）"""

    datetime_start, datetime_end = None, None
    success_logs, error_logs = [], []

    # nameのチェック
    error_logs.extend(validate_name(name))

    if not datetime_start_str:
        error_logs.append("開始日時を入力してください")
    if not datetime_end_str:
        error_logs.append("終了日時を入力してください")

    if datetime_start_str and datetime_end_str:
        # 受け取った文字列の日時をdatetime型に変換
        datetime_start = datetime.strptime(datetime_start_str, "%Y-%m-%d %H:%M")
        datetime_end = datetime.strptime(datetime_end_str, "%Y-%m-%d %H:%M")

        if datetime_start > datetime_end:
            error_logs.append("開始日時は終了日時より前に指定してください")

    if not error_logs:
        # dbに追加
        db.add(
            engine,
            Schedule(
                name=name, datetime_start=datetime_start, datetime_end=datetime_end
            ),
        )
        success_logs.append("スケジュールの保存に成功しました")

    context = {
        "request": request,
        "success_logs": success_logs,
        "error_logs": error_logs,
    }
    return templates.TemplateResponse("add.html", context=context)


def validate_name(name: str) -> list[str]:
    """nameをチェックする関数"""
    logs: list[str] = []
    if not name:
        logs.append("スケジュール名を入力してください")
    elif len(name) > 30:
        logs.append("スケジュール名は30文字以内にしてください")
    return logs
