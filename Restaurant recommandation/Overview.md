# Study Overview 

---------------

The purpose of this study is to use machine learning technics to implement a restaurant recommendation system. The inspiration really comes from a real life problem. I lived in a small town just outside of Boston Area; with limited food options, I was wonder what are some other options I should choose. 

After extensive research, I picked three algothrims to implement

- [K nearest Neighbor](https://en.wikipedia.org/wiki/K-nearest_neighbors_algorithm)
- [Explicit Alternative Least Square](https://spark.apache.org/docs/2.2.0/ml-collaborative-filtering.html)
- [Implicit Alternative Least Square](https://spark.apache.org/docs/2.2.0/ml-collaborative-filtering.html)

Of the three algothrims here, K nearest Neighbor is the easiest, following by two versions of ALS. All of them are examples of [collaborative filtering algothrim](https://en.wikipedia.org/wiki/Collaborative_filtering), which basically use other people ratings and review to compare those of your own's and give recommendations based on similarity in pattern.

The goal of this study is to find out my favourite restaurant given my current restaurant preference. In the study, you will see how the result of each algothrim differs from each other; and I will compare those results to what yelp offers on their own app to see if there if the algothrim actually reflects Yelp's recommendation strategy.

So, with out further due, let's jump into the analysis. 


## Next Section
[Data Source]
