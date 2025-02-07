from datetime import datetime


def get_current_week_type() -> str:
    if datetime.now().isocalendar().week % 2 == 0:
        return "верхній"
    else:
        return "нижній"
