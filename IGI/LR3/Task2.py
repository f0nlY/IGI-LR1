import math

def task2():
    """
    Task 2 (Variant 25): Read integers one by one, sum every second one.
    Loop ends when user enters 1.

    Input:
        integers entered by user one by one (int)
        sentinel value: 1 (stops the loop)

    Output:
        Prints every second number and their sum.
    """

    numbers = []  # list of all entered numbers (without sentinel)

    while True:
        try:
            num = int(input("Enter integer (1 to stop): "))
        except ValueError:
            print("Enter a valid integer")
            continue

        if num == 1:
            break

        numbers.append(num)

    # collect every second element (index 1, 3, 5...)
    second_numbers = []
    for i in range(len(numbers)):
        if i % 2 == 1:
            second_numbers.append(numbers[i])

    # sum every second element
    total = 0
    for n in second_numbers:
        total += n

    print("Every second number:", second_numbers)
    print("Sum of every second number:", total)


task2()
