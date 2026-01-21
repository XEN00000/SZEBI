import regex

def validate_name(name: str) -> None:
    pattern = regex.compile('^[a-z][a-z0-9-]*$')
    if not pattern.fullmatch(name):
        raise ValueError(f'device name has to start with a letter, and can contain only lowercase letter, digits and dashes. got: {name}')

def parse_bool(value: str) -> bool | None:
    if value is None:
        return None
    if value.lower() in ("yes", "true", "t", "1"):
        return True
    elif value.lower() in ("no", "false", "f", "0"):
        return False
    else:
        return None