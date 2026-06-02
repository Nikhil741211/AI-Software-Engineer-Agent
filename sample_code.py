def divide(a, b):
    try:
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            raise TypeError("Both inputs must be numbers")
        if b == 0:
            return float('inf')
        return a / b
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def safe_divide(a, b):
    return divide(a, b)

def main():
    print(safe_divide(10, 0))
    print(safe_divide(10, 'a'))

if __name__ == "__main__":
    main()