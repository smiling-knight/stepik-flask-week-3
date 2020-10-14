import json
from enum import Enum
from collections import OrderedDict

from defaults import DB_NAME, REQUESTS_FILE


class WorkingDays(Enum):
    mon = 1
    tue = 2
    wed = 3
    thu = 4
    fri = 5
    sat = 6
    sun = 7


class JsonHandler:
    @classmethod
    def _read(cls, fname: str):
        with open(fname, encoding="utf-8") as fp:
            return json.load(fp)

    @classmethod
    def _write(cls, fname: str, data) -> None:
        with open(fname, "w", encoding="utf-8") as fp:
            json.dump(data, fp, ensure_ascii=False)

    @classmethod
    def read_db(cls) -> dict:
        return cls._read(fname=DB_NAME)

    @classmethod
    def write_db(cls, data) -> None:
        cls._write(fname=DB_NAME, data=data)

    @classmethod
    def write_request(cls, data):
        try:
            current: list = cls._read(fname=REQUESTS_FILE)
        except FileNotFoundError:
            cls._write(fname=REQUESTS_FILE, data=[data])
        else:
            current.append(data)
            cls._write(fname=REQUESTS_FILE, data=current)


def get_working_days(schedule: dict) -> OrderedDict:
    # sorted by days
    sorted(schedule, key=lambda x: getattr(WorkingDays, x).value)
    return OrderedDict({k: v for k, v in schedule.items() if max(v.values())})
