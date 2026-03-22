def task5():
    """
    Task 5 (Variant 25): Operations on a list of real numbers.

    Input:
        n    - size of the list entered by user (int, > 0)
        list - real numbers entered by user one by one (float)

    Output:
        - The element with minimum absolute value.
        - Sum of elements between the first and last positive elements (exclusive).
    """

    #input size of the list
    while True:
        try:
            n = int(input("Enter size of the list (n > 0): "))
            if n > 0:
                break
            print("Enter a positive integer for n")
        except ValueError:
                print("Enter a valid integer for n")

    # input list elements  
    numbers = []
    for i in range(n):
         while True:
              try:
                num = float(input(f"Enter element [{i}]: "))
                numbers.append(num)
                break
              except ValueError:
                print("Enter a valid float for the element")

    print("List: ", numbers)
    # sum between first and last positive elements
    # find indices of all positive elements
    positive_indices = []
    for i in range(len(numbers)):
        if numbers[i] > 0:
            positive_indices.append(i)

    if len(positive_indices) < 2:
        print("Sum between first and last positive: fewer than 2 positive elements, sum is 0")
    else:
        first = positive_indices[0]
        last = positive_indices[-1]

        between = []
        for i in range(first + 1, last):  # exclusive of first and last
            between.append(numbers[i])

        total = 0
        for x in between:
            total += x

        print("First positive at index", first, ":", numbers[first])
        print("Last positive at index", last, ":", numbers[last])
        print("Elements between:", between)
        print("Sum between first and last positive:", total)


task5()
                              