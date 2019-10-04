import django.dispatch

report_created = django.dispatch.Signal(providing_args=["report"])
