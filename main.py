import os
from flask import Flask, request, Request

from db import database, get_reading_list, add_reading, Reading, ReadingType
from datetime import datetime, timezone

app = Flask(__name__)
app_timezone = timezone.utc


def _parse_isodatetime_string(dtstr: str, default_tz: timezone):
    dt = datetime.fromisoformat(dtstr)
    if dt is None:
        dt = dt.replace(tzinfo=default_tz)
    else:
        dt = dt.astimezone(default_tz)
    return dt


def _parse_post_data(request_data: bytes) -> list[Reading]:
    try:
        ret = []
        str_data = request.data.decode()
        for line in str_data.splitlines():

            line_parts = line.split(" ")
            if len(line_parts) != 3:
                raise Exception("Invalid format")

            # parse timestamp
            timestamp = int(line_parts[0])

            # parse reading type
            reading_type = line_parts[1]
            reading_type = ReadingType(reading_type)

            # parse reading float
            value = float(line_parts[2])

            reading = Reading(timestamp=timestamp)
            match reading_type:
                case ReadingType.Voltage:
                    reading.voltage = value
                case ReadingType.Current:
                    reading.current = value

            ret.append(reading)

        return ret

    except Exception as e:
        print(e)
        raise Exception("Could not parse data")


def _format_output_time(timestamp: int, is_day: bool = False):
    if is_day:
        raise NotImplementedError()

    dt = datetime.fromtimestamp(timestamp)

    return dt.strftime("%Y-%m-%dT%H:%M:%S.") + dt.strftime("%f")[:3] + "Z"


@app.post("/data")
def post_data():

    try:
        input_data = _parse_post_data(request.data)

        for reading in input_data:
            add_reading(reading.timestamp, reading)

        return {"success": True}

    except Exception as e:
        print(e)
        return {"success": False}


@app.get("/data")
def get_data():

    try:
        from_ = _parse_isodatetime_string(
            request.args.get('from'), app_timezone)
        to = _parse_isodatetime_string(request.args.get('to'), app_timezone)
        from_timestamp = int(from_.timestamp())
        to_timestamp = int(to.timestamp())

        print(from_timestamp, to_timestamp)

        readings = get_reading_list(from_timestamp, to_timestamp)

        if len(readings) == 0:
            return []

        ret_json = []

        for reading in readings:

            # check voltage
            if reading.voltage is not None:
                ret_json.append({
                    "time": _format_output_time(reading.timestamp),
                    "name": ReadingType.Voltage,
                    "value": reading.voltage
                })
            if reading.current is not None:
                ret_json.append({
                    "time": _format_output_time(reading.timestamp),
                    "name": ReadingType.Current,
                    "value": reading.current
                })

        return ret_json
    except Exception as e:
        print(e)
        return {"success": False}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(port=port, debug=True)
