def divide(a, b):
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("Both inputs must be numbers")
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero")
    return a / b

def safe_divide(a, b):
    try:
        return divide(a, b)
    except Exception as e:
        print(f"An error occurred in safe_divide: {e}")
        return None

def main():
    print(safe_divide(10, 0))
    print(safe_divide(10, 'a'))

if __name__ == "__main__":
    main()