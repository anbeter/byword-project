from django.db import models


class DayOfWeek(models.IntegerChoices):
    SUNDAY = 1, "Sunday"
    MONDAY = 2, "Monday"
    TUESDAY = 3, "Tuesday"
    WEDNESDAY = 4, "Wednesday"
    THURSDAY = 5, "Thursday"
    FRIDAY = 6, "Friday"
    SATURDAY = 7, "Saturday"

    @classmethod
    def weekdays(cls):
        return [
            cls.MONDAY,
            cls.TUESDAY,
            cls.WEDNESDAY,
            cls.THURSDAY,
            cls.FRIDAY,
        ]

    @classmethod
    def weekdays2(cls):
        return [
            cls.MONDAY,
            cls.TUESDAY,
            cls.WEDNESDAY,
            cls.THURSDAY,
            cls.FRIDAY,
            cls.SATURDAY,
        ]

    @classmethod
    def weekend(cls):
        return [cls.SATURDAY, cls.SUNDAY]
    
    @classmethod
    def business_choices(cls):
        return [
            (day.value, day.label)
            for day in cls
            if day in cls.weekdays()
        ]
    
    @classmethod
    def business_choices2(cls):
        return [
            (day.value, day.label)
            for day in cls
            if day in cls.weekdays2()
        ]