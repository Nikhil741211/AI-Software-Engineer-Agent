def divide(a, b):
    try:
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            raise TypeError("Both inputs must be numbers")
        if b == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        return a / b
    except TypeError as e:
        print(f"TypeError: {e}")
        return None
    except ZeroDivisionError as e:
        print(f"ZeroDivisionError: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

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