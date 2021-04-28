import sqlalchemy as sa

from timeschedule.models import Schedule

# SQLAlchemyの機能を使ってDBのテーブル定義をします
# cf. https://docs.sqlalchemy.org/en/14/core/schema.html
metadata = sa.MetaData()
schedules_table = sa.Table(
    "schedules",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column("name", sa.String(256), nullable=False),
    sa.Column("datetime_start", sa.DateTime, nullable=False),
    sa.Column("datetime_end", sa.DateTime, nullable=False),
    sa.Column(
        "created_at",
        sa.DateTime,
        nullable=False,
        server_default=sa.sql.functions.current_timestamp(),
    ),
)


def create_table(engine: sa.engine.Connectable) -> None:
    """テーブル定義に従ってテーブル作成をする"""
    metadata.create_all(engine)


# SQLの実行はSQLAlchemy Core APIを使っています
# cf. https://docs.sqlalchemy.org/en/14/core/tutorial.html
def find_all(engine: sa.engine.Connectable) -> list[Schedule]:
    """すべてのメッセージを取得する"""
    with engine.connect() as connection:
        query = sa.sql.select(
            (
                schedules_table.c.id,
                schedules_table.c.name,
                schedules_table.c.datetime_start,
                schedules_table.c.datetime_end,
                schedules_table.c.created_at.label("createdAt"),
            )
        )
        return [Schedule(**m) for m in connection.execute(query)]


def add(engine: sa.engine.Connectable, Schedule: Schedule) -> None:
    """メッセージを保存する"""
    with engine.connect() as connection:
        query = schedules_table.insert()
        connection.execute(query, Schedule.dict())


def delete_all(engine: sa.engine.Connectable) -> None:
    """メッセージをすべて消す（テスト用）"""
    with engine.connect() as connection:
        connection.execute(schedules_table.delete())
