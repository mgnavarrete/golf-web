from core.views import _local_today, _day_bounds
from core.models import CourseEntry, RangeOrder, CashClosure
import xlsxwriter
from io import BytesIO
from django.utils import timezone
from datetime import datetime, time

date_from = _local_today()
date_to = _local_today()

start_dt, _ = _day_bounds(date_from)
_, end_dt = _day_bounds(date_to)

course_qs = CourseEntry.objects.filter(created_at__gte=start_dt, created_at__lte=end_dt).select_related("created_by")
range_qs = RangeOrder.objects.filter(created_at__gte=start_dt, created_at__lte=end_dt).select_related("created_by")
closures_qs = CashClosure.objects.filter(operational_date__gte=date_from, operational_date__lte=date_to)

output = BytesIO()
workbook = xlsxwriter.Workbook(output, {"in_memory": True})

date_fmt = workbook.add_format({"num_format": "yyyy-mm-dd"})
ws_course = workbook.add_worksheet("Cancha")
for row, item in enumerate(course_qs, start=1):
    local_dt = timezone.localtime(item.created_at)
    user_name = f"{item.created_by.first_name} {item.created_by.last_name}".strip() or item.created_by.email
    ws_course.write_datetime(row, 0, local_dt, date_fmt)

ws_closure = workbook.add_worksheet("Cierres")
for row, item in enumerate(closures_qs, start=1):
    user_name = f"{item.closed_by.first_name} {item.closed_by.last_name}".strip() or item.closed_by.email
    ws_closure.write_datetime(row, 0, datetime.combine(item.operational_date, time.min), date_fmt)


workbook.close()
print("Success!")
