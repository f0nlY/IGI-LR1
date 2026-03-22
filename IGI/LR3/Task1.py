import math

def task1():

    """
    Task 1 (Variant 25): Compute e^x using its power series expansion.
    Formula: e^x = sum(x^n / n!, n=0..inf)

    Input:
        x   - real number entered by user (any float)
        eps - precision, entered by user (float, 0 < eps < 1)

    Output:
        Prints x, F(x) computed by series, number of terms used,
        and math.exp(x) for comparison.
    """

    while True:
        try:
            x = float(input("Enter x: "))
            break
        except ValueError: 
            print("Enter a valid float for x")

    while True:
        try:
            eps = float(input("Enter eps (0 < eps < 1)"))
            break
        except ValueError:
            print("Enter a valid float for eps")

    max_iterations = 500
    series_sum = 1.0 # First term of the series (n=0)
    term = 1.0 # To store the current term x^n / n!
    n = 1

    while n <= max_iterations:
        term *= x / n
        series_sum += term # Add the current term to the sum
        n += 1
        if abs(term) < eps:
            break

    print(f"\n+{'─'*10}+{'─'*6}+{'─'*15}+{'─'*15}+{'─'*10}+")
    print(f"|{'x':^10}|{'n':^6}|{'F(x)':^15}|{'Math F(x)':^15}|{'eps':^10}|")
    print(f"+{'─'*10}+{'─'*6}+{'─'*15}+{'─'*15}+{'─'*10}+")
    print(f"|{x:^10}|{n-1:^6}|{series_sum:^15.10f}|{math.exp(x):^15.10f}|{eps:^10}|")
    print(f"+{'─'*10}+{'─'*6}+{'─'*15}+{'─'*15}+{'─'*10}+")


task1()


