def task4():
    """
    Task 4 (Variant 25): Analyze a given text string. No regex used.

    Input:
        No user input. Text is hardcoded as per task requirements.

    Output:
        a) Count of words with minimum length and the words themselves.
        b) All words followed by a period.
        c) The longest word ending with 'r'.
    """

    text = ("So she was considering in her own mind, as well as she could, for the "
            "hot day made her feel very sleepy and stupid, whether the pleasure of "
            "making a daisy-chain would be worth the trouble of getting up and "
            "picking the daisies, when suddenly a White Rabbit with pink eyes ran "
            "close by her.")

    tokens = text.split()  # split into tokens (words may have punctuation)

    # clean each word from punctuation for analysis
    words = []
    for token in tokens:
        clean = token.strip(".,!?;:")
        if clean:
            words.append(clean)

    # a) words with minimum length
    min_len = len(words[0])
    for w in words:
        if len(w) < min_len:
            min_len = len(w)

    min_words = []
    for w in words:
        if len(w) == min_len:
            min_words.append(w)

    print("a) Minimum word length:", min_len)
    print("   Words with minimum length:", min_words)
    print("   Count:", len(min_words))


   # b) all words followed by a period

    period_words = []    
    for token in tokens:
        if token.endswith('.'):
            period_words.append(token.strip(".,!?;:"))

    print("\nb) Words followed by a period:", period_words)

    #c) longest word ending with 'r'
    longest_r = ""
    for w in words:
        if w.lower().endswith("r"):
            if len(w) > len(longest_r):
                longest_r = w
    if longest_r:
        print("\nc) Longest word ending with 'r':", longest_r)
    else:
        print("\nc) No words ending with 'r' found.")


task4()            


