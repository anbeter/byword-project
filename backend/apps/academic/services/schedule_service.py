from collections import defaultdict
from datetime import time
from django.urls import reverse

from apps.academic.models import ClassSchedule, BlockedSchedule


START_HOUR = 8
END_HOUR = 18
PIXELS_PER_MINUTE = 1  # 60px por hora


def time_to_minutes(t):
    return t.hour * 60 + t.minute


# def generate_time_slots():
#     return [time(hour, 0) for hour in range(START_HOUR, END_HOUR + 1)]

def generate_time_slots():
    slots = []
    for index, hour in enumerate(range(8, 18)):
        slots.append({
            "time": time(hour, 0),
            "top": index * 62  # 👈 AQUI resolve tudo
        })
    return slots


def get_weekly_schedule_grid():
    grid = defaultdict(list)
    occupied = defaultdict(set)

    start_day_minutes = START_HOUR * 60

    # ======================
    # AULAS
    # ======================
    for item in ClassSchedule.objects.filter(is_active=True):

        if not item.start_time or not item.end_time:
            continue

        start_hour = item.start_time.hour
        end_hour = item.end_time.hour

        for h in range(start_hour, end_hour):
            occupied[item.day_of_week].add(h)
            
        start_min = time_to_minutes(item.start_time)
        end_min = time_to_minutes(item.end_time)

        top = ((start_min - start_day_minutes)+15) * PIXELS_PER_MINUTE
        top +=2
        height = (end_min - start_min) * PIXELS_PER_MINUTE
        height -= 7

        grid[item.day_of_week].append({
            "type": "class",
            "label": str(item.class_obj),
            "start": item.start_time,
            "end": item.end_time,
            "top": top,
            "height": height,
            "url": reverse("admin:academic_class_change", args=[item.class_obj.id]),
        })

    # ======================
    # BLOQUEIOS
    # ======================
    for block in BlockedSchedule.objects.filter(is_active=True):

        start_dt, end_dt = block.get_start_end()
        if not start_dt or not end_dt:
            continue

        start_hour = start_dt.time().hour
        end_hour = end_dt.time().hour

        for h in range(start_hour, end_hour):
            occupied[block.day_of_week].add(h)

        start_time = start_dt.time()
        end_time = end_dt.time()

        start_min = time_to_minutes(start_time)
        end_min = time_to_minutes(end_time)

        top = (start_min - start_day_minutes) * PIXELS_PER_MINUTE
        top +=5
        height = (end_min - start_min) * PIXELS_PER_MINUTE
        height -= 7

        grid[block.day_of_week].append({
            "type": "blocked",
            "label": block.reason or "Blocked",
            "start": start_time,
            "end": end_time,
            "top": top,
            "height": height,
            "url": reverse("admin:academic_blockedschedule_change", args=[block.id]),
        })

    # ======================
    # ORDENAR POR HORÁRIO
    # ======================
    for day in grid:
        grid[day].sort(key=lambda x: x["top"])

    times = generate_time_slots()

        
    return grid, times, occupied