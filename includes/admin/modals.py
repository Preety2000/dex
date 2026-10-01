from datetime import date, datetime

divider = "_"


def emptyMessage(message, types):
    return f'This data cannot be {types or "save"} because <b>{message}</b> is empty.'


def checked(acrion, resource_dictionary):
    if acrion:
        resource_dictionary.update({"checked": "checked"})
        return True


# Custom function to handle datetime and date serialization
def CustomJSONEncoder(obj):
    if isinstance(obj, (datetime, date)):
        # return obj.strftime("%Y-%m-%dT%H:%M:%S%z")
        return obj.isoformat()

    raise TypeError("Type not serializable")
