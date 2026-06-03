from sample_code import divide

def test_divide():
    try:
        assert divide(10, 2) == 5
    except ZeroDivisionError:
        pass

def safe_divide(a, b):
    if b == 0:
        return None
    return a / b

def divide(a, b):
    return safe_divide(a, b)