from attr import dataclass


@dataclass
class CronDate:
    day_of_week: int
    hour: int
    minute: int
