def load_words_from_file(file_path):
    with open(file_path, 'r') as file:
        words = [line.strip() for line in file.readlines()]
    return words

# Usage
file_path = 'wordlist.txt'  # Replace with your actual file path
word_list = load_words_from_file(file_path)

print(word_list) 