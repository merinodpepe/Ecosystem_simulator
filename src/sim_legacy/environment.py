import numpy as np
from dataclasses import dataclass, field
from typing import Callable

MONTH_NAMES = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]


@dataclass
class Environment:
    total_days: int = 365
    current_day: int = 0
    year: int = 0

    snow_line_m: float = 2700.0
    temperature_base_c: float = 5.0
    precipitation_mm: float = 0.0

    snow_fn: Callable = lambda elev, day: 0.0
    temp_fn: Callable = lambda elev, day: 5.0

    @property
    def month(self) -> int:
        return (self.current_day % 365) // 30

    @property
    def season(self) -> str:
        d = self.current_day % 365
        if 60 <= d < 152:
            return "spring"
        elif 152 <= d < 244:
            return "summer"
        elif 244 <= d < 335:
            return "autumn"
        else:
            return "winter"

    @property
    def day_of_year(self) -> int:
        return self.current_day % 365

    def step(self):
        self.current_day += 1
        if self.current_day % 365 == 0:
            self.year += 1

    def get_snow_cover(self, elevation_m: float) -> float:
        return self.snow_fn(elevation_m, self.current_day)

    def get_temperature(self, elevation_m: float) -> float:
        return self.temp_fn(elevation_m, self.current_day)


def default_snow_fn(elevation_m: float, day: int) -> float:
    doy = day % 365
    season_amplitude = np.cos(2 * np.pi * (doy - 15) / 365)
    snow_line = 2400 + 600 * (season_amplitude + 1) / 2
    if elevation_m < snow_line:
        return 0.0
    return min(1.0, (elevation_m - snow_line) / 800.0)


def default_temp_fn(elevation_m: float, day: int) -> float:
    doy = day % 365
    base_temp = 5.0 + 10.0 * np.cos(2 * np.pi * (doy - 182) / 365)
    lapse_rate = -0.0065
    return base_temp + lapse_rate * max(0.0, elevation_m - 1000.0)
