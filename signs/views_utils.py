import requests
from datetime import datetime, timedelta


def get_weekdays(api_url: str, location_id: str, num_weeks: int) -> list[dict]:
    print("I'm getting weekdays")
    response = requests.get(
        api_url, params={"lid": location_id, "weeks": num_weeks, "format": "json"}
    )
    data = response.json()
    print(data)
    weekdays = [
        *data["weeks"][0],
        *data["weeks"][1],
    ]
    weekdays = weekdays[1:8]

    formatted_weekdays = [
        {
            "date": datetime.strptime(item["date"], "%Y-%m-%d") - timedelta(hours=7),
            **item,
        }
        for item in weekdays
    ]

    sorted_weekdays = sorted(formatted_weekdays, key=lambda x: x["date"])

    return sorted_weekdays
