from dataclasses import dataclass
from enum import StrEnum
from threading import Lock
import bisect


class ReadingType(StrEnum):
    Voltage = "Voltage"
    Current = "Current"


@dataclass
class Reading():
    timestamp: int
    voltage: float | None = None
    current: float | None = None


# This is a fake database which stores data in-memory while the process is running
# Feel free to change the data structure to anything else you would like
database: dict[int, Reading] = {}
write_lock = Lock()


def add_reading(key: int, reading: Reading) -> None:
    """
    Store a reading in the database using the given key
    """
    write_lock.acquire()

    if key in database:
        r = database[key]
    else:
        r = Reading(timestamp=key)

    if reading.current is not None:
        r.current = reading.current
    if reading.voltage is not None:
        r.voltage = reading.voltage

    database[key] = r

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

    if start_key == len(timestamps):
        return []

    if to >= timestamps[-1]:
        end_key = len(timestamps) - 1
    else:
        while timestamps[end_key] <= to:
            end_key += 1
        end_key -= 1

    ret = []
    for t in timestamps[start_key:end_key+1]:
        ret.append(database[t])

    return ret
