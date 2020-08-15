from stemming.porter2 import stem


def cleanse_text(text):
    if text:
        # whitespaces
        text = ' '.join(text.split())

        # stemming
        red_text = [stem(word) for word in text.split()]
        return ' '.join(red_text)
    else:
        return text


