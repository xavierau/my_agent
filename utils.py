import json
import time
import math
from typing import Any, Dict

from carparks.types import Point


def save_data_to_file(data: Any, file_path: str) -> None:
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2)
        print(f"Data has been written to {file_path}")
    except Exception as error:
        print(f"ERROR: An error occurred while trying to write to {file_path}:", error)


def load_data_from_file(file_path: str) -> Any:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as error:
        print(f"ERROR: An error occurred while reading the file: {error}")
        raise


def sleep(seconds: int) -> None:
    time.sleep(seconds)


def calculate_distance(point1: Point, point2: Point) -> float:
    R = 6371e3  # Radius of the Earth in meters
    φ1 = math.radians(point1.lat)
    φ2 = math.radians(point2.lat)
    Δφ = math.radians(point2.lat - point1.lat)
    Δλ = math.radians(point2.lng - point1.lng)

    a = math.sin(Δφ / 2) ** 2 + math.cos(φ1) * math.cos(φ2) * math.sin(Δλ / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c  # Distance in meters


# Example usage
point1 = Point(lat=50.06638889, lng=-5.71472222)
point2 = Point(lat=58.64388889, lng=-3.07000000)
distance = calculate_distance(point1, point2)
print(distance)  # Distance in meters
