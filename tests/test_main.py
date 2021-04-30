from timeschedule.main import validate_name


def test_validate_name_name_is_normal():
    name = "スケジュール名"
    assert validate_name(name) == []


def test_validate_name_name_is_none():
    name = ""
    assert validate_name(name) == ["スケジュール名を入力してください"]


def test_validate_name_length_30():
    name = "a" * 30
    assert validate_name(name) == []


def test_validate_name_length_31():
    name = "a" * 31
    assert validate_name(name) == ["スケジュール名は30文字以内にしてください"]
