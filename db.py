from dataclasses import dataclass
from enum import StrEnum
from threading import Lock
import bisect


class ReadingType(StrEnum):
    Voltage = "Voltage"
    Current = "Current"


@dataclass
class ReadingInstance():
    reading_type: ReadingType
    value: float


@dataclass
class Reading():
    timestamp: int
    readings: list[ReadingInstance]


# This is a fake database which stores data in-memory while the process is running
# Feel free to change the data structure to anything else you would like
database: dict[int, Reading] = {}
write_lock = Lock()


def add_reading(key: int, reading: Reading) -> None:
    """
    Store a reading in the database using the given key
    """
    write_lock.acquire()

    if key not in database:
        database[key] = reading
    else:
        r = database[key]
        rlist = r.readings
        rlist.append(reading)

    write_lock.release()


def get_reading(key: int) -> Reading | None:
    """
    Retrieve a reading from the database using the given key
    """
    return database.get(key)


def get_reading_list(from_: int, to: int) -> list[Reading]:

    timestamps = sorted(database.keys())
    start_key = bisect.bisect_left(timestamps, from_)
    end_key = start_key

    print(timestamps)

    while end_key < len(timestamps) and timestamps[end_key] <= to:
        end_key += 1

    end_key -= 1

    print(start_key, end_key)

    return []
