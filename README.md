# Enhanced-Information-Retrieval-System-with-Query-Expansion

This project was a team effort for the COMS6111 - Advanced Database Systems course at Columbia University.

# Team Members
Ronitt Mehra (UNI: rm4084) 
Yueran Ma (UNI: ym2876)

# How to run the program ?

`python3 feedback.py <google api key> <google engine id> <precision> <query>`

# Internal Working
The code calls the get_query() function in the main() function. get_query() essentially collects the API_KEY, ENGINE_ID, desired precision, and the initial query as command line arguments. Furhtermore, it checks whether all the arguments have been provided. For easier testing and execution, get_query() allows the user to only input the desired precision and the initial query, if the user has saved the API_KEY and the ENGINE_ID as environmental variables.

The loop() function then performs some crucial initialisation steps, such as loading a list of all the stop words and initialising the user inputs. Afterwards, this function enters an infinite loop, which stops when either the user has achieved the desired precision or when there are no relevant results.

In each iteration, we first use the search() function to fetch result from Google Search API. The search() function returns the top 10 results, each of which contain the title, URL and a summary of the page. The print_param() and print_res() functions present the search parameters and search result to users in command line.

For each of the 10 results, we save a bag of words for all the relevant and non-relevant documents. After receiving the feedback, we first check if the precision is equal to or higher than the desired precision. If not, then we apply Rocchio's Algorithm, and further expand the query before moving onto the next iteration.

# Method for Query Expansion

We have implemented Rocchio's Algorithm. the algorithm is as follows:

$$
Q' = alpha*Q + \frac{beta}{|D_r|}*(\sum_{d_j \in D_r} d_j) - \frac{gamma}{|D_{nr}|}*(\sum_{d_j \in D_{nr}} d_j)
$$

Where, 

Q’ = new query vector

Q = original query vector

$𝐷_𝑟$ = set of all relevant documents

$𝐷_{𝑛𝑟}$ = set of all non-relevant documents

alpha, beta, gamma = Rocchio Algorithm parameters

The expand_query() function implements the Rocchio's Algorithm.
The relevant_documents_sum and non_relevant_documents_sum are bag of words vectors that contain the aggregation of all the bag of words corresponding to the relevant documents and the non-relevant documents respectively. We have further implemented a normalisation of the above obtain aggregate bag of words vectors corresponding to the relevant documents and the non-relevant documents. This is done to ensure that adjustments made to the query are independent of the scale.

To implement the Rocchio's algorithm, the beta coefficient is multiplied by the average vector corresponding to the relevant documents, and gamma is multiplied by the average vector corresponding to the non-relevant documents. The scaled term corresponding to relevant documents is then added to original query vector, and the scaled term corresponding to the non-relevant documents is subtracted from the original query vector. This is done to ensure that the new query vector generated is closer to the relevant documents, and further from the non-relevant documents.
After adjusting the query vector with Rocchio's Algorithm, the new query vector contains terms from both the original query as well as the terms from the relevant documents. After finding out the words that have been added to the query vector, we prioritize the words with more relevance. This is done by sorting the new terms by weight in decreasing order.
Then, the first two terms (most relevant ones) in this sorted list of terms are appended to the query to finally expand the original query. We also make sure that we do not add more than two terms to the query.

API_KEY=AIzaSyDG40Sow4mvOr1uKxx6kygmp-mqb6bhFu8 
ENGINE_ID=257df0a8fe2bd4997


