import re
import string
import pickle
import argparse
from typing import List, Dict
from collections import Counter
from unicodedata import normalize


def get_sentences_from_document(filename: str) -> List[str]:
    """ Load the target text file and return a list containing every sentence in it. """
    with open(filename, "r") as file:
        raw_text = file.read()
        sentences = raw_text.strip().split("\n")
    return sentences

def get_vocabulary_count(sentences: List[str]) -> Dict[str, int]:
    """ Return a mapping: {unique_word -> number_of_occurrences} based on the given sentences. """
    voc = Counter()
    for sentence in sentences:
        words = sentence.split()
        voc.update(words)
    return voc

def reduce_vocab(vocab, threshold):
    """ Return a set of words which have occurred at least the `threshold` number of times. """
    return set([word for word, cnt in vocab.items() if cnt >= threshold])

#Updating the data set
def update_dataset(sentences, vocab):
    """ Take the original sentences and then use the cleaned and reduced vocabulary to update them. """
    new_sentences = []
    for line in sentences:
        new_words = []
        for t in line.split():
            if t in vocab:
                new_words.append(t)
            else:
                new_words.append("uup")
        new_words = [word for word in new_words if word !="s"]
        new_line = " ".join(new_words)
        new_sentences.append(new_line)
    return new_sentences

def clean_sentences(lines: List[str]) -> List[str]:
    """ Normalize/clean the input lines by:
            1. Converting phonetic Latin characters to their simple English form. E.g. o` -> o
            2. Making all words lowercase.
            3. Removing punctuation characters.
            4. Removing all non-printable characters.
            5. Removing all numeric characters. """
    cleaned_sentences =  []
    re_pat = re.compile("[^%s]" % re.escape(string.printable))  # filter printable chars
    table = str.maketrans("", "", string.punctuation)
    # `table` is a dictionary mapping the ascii value of each punctutation character to None.
    # We use this to remove punctutation characters in the code below.
    for line in lines:
        line = normalize("NFD", line).encode("ascii", "ignore").decode("UTF-8")  # normalizing chars such as o` and o.
        words = line.split()  # tokenize on whitespaces
        lowercase_words = [word.lower() for word in words]  # lowercase all the words
        punctuationless_words = [word.translate(table) for word in lowercase_words]  # remove all the punctuation marks
        printable_words = [re_pat.sub("", word) for word in punctuationless_words]  # remove non-printable chars
        non_numeric_words = [word for word in printable_words if word.isalpha()]  # remove numbers
        cleaned_sentences.append(" ".join(non_numeric_words))
    return cleaned_sentences

def preprocess_file(input_filename, output_filename, vocab_reduction_threshold=4):
    """ Take one of the original input files and then completely preprocess it. """
    # TODO: Add a check to skip steps if cleaned data exists.
    raw_sentences = get_sentences_from_document(input_filename)
    cleaned_sentences = clean_sentences(raw_sentences)
    pickle.dump(cleaned_sentences, open(output_filename + ".pkl", "wb"))
    vocab = get_vocabulary_count(cleaned_sentences)
    reduced_vocab = reduce_vocab(vocab, vocab_reduction_threshold)
    new_data = update_dataset(cleaned_sentences, reduced_vocab)
    pickle.dump(new_data, open(output_filename + ".reduced.pkl", "wb"))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="path of file to process.", default="Input.txt")
    parser.add_argument("-o", "--output", help="path of file to write processed data to process without an extension.", default="Output.txt")
    parser.add_argument("-vrt", "--vocab_reduction_threshold", help="set the vocab reduction threshold.", default=4)
    args = parser.parse_args()
    preprocess_file(args.input, args.output, args.vocab_reduction_threshold)
