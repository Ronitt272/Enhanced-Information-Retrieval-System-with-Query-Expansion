import sys, os, re

from googleapiclient.discovery import build
from collections import Counter
import math


def get_query():
    api_key = os.environ.get('API_KEY', None)
    engine_id = os.environ.get('ENGINE_ID', None)

    if len(sys.argv) == 5:
        api_key, engine_id, precision, query = sys.argv[1:5]
    elif len(sys.argv) == 3:
        precision, query = sys.argv[1:3]
    else:
        print("Error: Please provide either command line arguments in the format '<google api key> <google engine id> <precision> <query>', or set the required environment variables and provide arguments in the format '<precision> <query>'.")
        sys.exit(1)
    
    return api_key, engine_id, float(precision), query


def search(api_key, engine_id, query):
    service = build(
        "customsearch", "v1", developerKey=api_key
    )

    res = (
        service.cse()
        .list(
            q=query,
            cx=engine_id,
        )
        .execute()
    )
    return res

def print_param(user_input):
    api_key, engine_id, precision, query = user_input
    print("Parameters:")
    print(f"Client key  = {api_key}")
    print(f"Engine key  = {engine_id}")
    print(f"Query       = {query}")
    print(f"Precision   = {precision}")
    print("\nGoogle Search Results:")
    print("=======================")

def print_res(i, url, title, summary):
    print(f"Result {i+1}")

    print("[")
    print(f"  URL: {url}")
    print(f"  Title: {title}")
    print(f"  Summary: {summary}")
    print("]\n")

def print_feedback(prev_query, curr_precision, desired_precision, new_query=''):
    print("")
    print("FEEDBACK SUMMARY")
    print("=======================")
    print(f"Query: {prev_query}")
    print(f"Precision: {curr_precision}")
    if curr_precision >= desired_precision:
        print("Target precision reached!")
    elif curr_precision == 0:
        print("Below desired precision, but can no longer augment the query")
    else:
        print(f"Still below the desired precision of {desired_precision}")
        print("Indexing results ....")
        print(f"Augmenting query to: {new_query}")

def load_stop_words(file_path):
    with open(file_path, 'r') as file:
        stop_words = [line.strip() for line in file]
    return stop_words

def str_to_bag(input_str, stop_words):
    cleaned_str = re.sub(r'[^a-zA-Z0-9\s]', '', input_str.lower())
    words = cleaned_str.split()
    filtered_words = [word for word in words if word not in stop_words]
    word_freq = Counter(filtered_words)
    bag = {word: count for word, count in word_freq.items()}

    return bag

def merge_dicts(dict1, dict2):
    for k, v in dict2.items():
        if k in dict1:
            dict1[k] += v
        else:
            dict1[k] = v

def vector_normalization(vector):
    # As taught in the class, normalizing the vectors to get a more accurate judgement
    vector_length_square = 0.0
    for value in vector.values():
        vector_length_square += value**2
    vector_length = math.sqrt(vector_length_square)

    # normalizing using the above vector length calculated
    normalized_vector = {key: value/vector_length for key, value in vector.items() if vector_length > 0}
    return normalized_vector

def expand_query(query_vector, relevant_documents, non_relevant_documents):
    
    alpha = 1
    beta = 0.75
    gamma = 0.15

    relevant_documents_sum = Counter()
    non_relevant_documents_sum = Counter()

    for vector in relevant_documents:
        relevant_documents_sum.update(vector)
    for vector in non_relevant_documents:
        non_relevant_documents_sum.update(vector)
    
    # normalizing the resultant vectors for both relevant and non-relevant documents as obtained above
    relevant_documents_sum = vector_normalization(relevant_documents_sum)
    non_relevant_documents_sum = vector_normalization(non_relevant_documents_sum)

    # keeping counts of the relevant and non-relevant documents for rocchio algorithm
    Dr = len(relevant_documents)
    Dnr = len(non_relevant_documents)

    #expanded_query = Counter(query_vector)

    # implementing Rocchio Algorithm for Query expansion
    expanded_query = Counter({key: alpha*value for key, value in query_vector.items()})
    #print("expanded_query: ", expanded_query)
    expanded_query.update({key: beta*value/Dr for key, value in relevant_documents_sum.items()})
    expanded_query.subtract({key: gamma*value/Dnr for key, value in non_relevant_documents_sum.items()})
    normalized_expanded_query = vector_normalization(expanded_query)

    return normalized_expanded_query

def loop(user_input):
    api_key, engine_id, precision, query = user_input
    stop_words = load_stop_words('stop_words.txt')

    # converting the query to a list of words as it is a string
    query = query.split()

    while True:
        search_query = ' '.join(query)
        #print(search_query)
        res = search(api_key, engine_id, search_query)
        if len(query) == 1 and len(res['items']) < 10:
            print("Receive fewer than 10 results in the first iteration")
            sys.exit(1)

        curr_precision = 0

        print_param(user_input)

        word_bag = dict()

        non_relevant_documents = []
        relevant_documents = []
        query_vector = {}

        query_vector = Counter(str_to_bag(search_query, stop_words=stop_words))

        for i in range(10):
            url = res['items'][i]['formattedUrl']
            title = res['items'][i]['title']
            summary = res['items'][i]['snippet']
            print_res(i, url, title, summary)

            relevant = input("Relevant (Y/N)? ")
            if relevant == 'Y' or relevant == 'y':
                relevant_documents.append(Counter(str_to_bag(title+" "+summary, stop_words=stop_words)))
                curr_precision += 1

                # extracting bag of words from the title and summary of the document
                title_bag = str_to_bag(title, stop_words)
                summary_bag = str_to_bag(summary, stop_words)
                merge_dicts(word_bag, title_bag)
                merge_dicts(word_bag, summary_bag)

            else:
                non_relevant_documents.append(Counter(str_to_bag(title+" "+summary, stop_words=stop_words)))
                
        #for key, value in word_bag.items():
        #    print(f"{key}: {value}")

        if curr_precision == 0:
            print('No relevant results.')
            sys.exit(1)

        curr_precision /= 10
        if curr_precision >= precision:
            print_feedback(prev_query = search_query, curr_precision = curr_precision, desired_precision = precision)
            break

        # calling the below function, where Rocchio's Algorithm has been implemented
        new_query_vector = expand_query(query_vector, relevant_documents, non_relevant_documents)

        # Atmost 2 words can be appended, so selecting the best 2 words that will be appended
        words = [word for word in new_query_vector if word not in query]
        best_words = sorted(words, key=lambda word: new_query_vector[word], reverse=True)[:2]
        
        # expanding the query with the best two words that we were able to find
        query.extend(best_words)
        expanded_search_query = ' '.join(query)
        print_feedback(prev_query = search_query, curr_precision = curr_precision, desired_precision = precision, new_query = expanded_search_query)

def main():
    user_input = get_query()

    loop(user_input)


if __name__ == "__main__":
    main()