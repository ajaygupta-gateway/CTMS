SENSITIVE_KEYS = {"password", "token", "secret"}


def mask_sensitive_data(data):
    """
    Recursively mask sensitive fields in dicts/lists.
    """
    if isinstance(data, dict):
        return {
            key: ("******" if key.lower() in SENSITIVE_KEYS else mask_sensitive_data(value))
            for key, value in data.items()
        }

    if isinstance(data, list):
        return [mask_sensitive_data(item) for item in data]

    return data
