from collections import defaultdict
from apps.academic.models import ClassSchedule, BlockedSchedule


def get_weekly_schedule():
    schedule = defaultdict(list)

    # 🔹 aulas
    for item in ClassSchedule.objects.filter(is_active=True):
        schedule[item.day_of_week].append({
            "type": "class",
            "class": str(item.class_obj),
            "start_time": item.start_time,
            "end_time": item.end_time,
        })

    # 🔹 bloqueios
    for block in BlockedSchedule.objects.filter(is_active=True):
        schedule[block.day_of_week].append({
            "type": "blocked",
            "reason": block.reason,
            "start_time": block.start_time,
            "end_time": (
                block.get_start_end()[1].time()
            ),
        })

    # 🔹 ordenar por horário
    for day in schedule:
        schedule[day].sort(key=lambda x: x["start_time"])

    return dict(schedule)