PRIORITIES = {}

app_order = [
    'webapp',
    'ajax',
    'admin',
    'httptester',
    'logger',
    'locate',
    'signup',
    'danger',
]

i = 1
for app in app_order:
    PRIORITIES[app] = i
    i += 1