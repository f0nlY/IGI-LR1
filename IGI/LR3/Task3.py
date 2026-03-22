def task3():
    """
    Task 3 (Variant 25): Count words starting with a lowercase consonant.
    No regex used.

    Input:
        text - string entered by user (str)

    Output:
        Prints the count of words starting with a lowercase consonant
        and the list of such words.
    """

    vowels = "aeiou"
    alphabet = "abcdefghijklmnopqrstuvwxyz"

    text = input("Enter a string: ")
    words = text.split()  # split the input into words

    count = 0
    consonant_words = []

    for word in words:
        first_letter = word[0] # get the first letter of the word
        if first_letter in alphabet and first_letter not in vowels:
            count += 1
            consonant_words.append(word)
    print("Words starting with lowercase consonant:", consonant_words)
    print("Count:", count)

task3()
