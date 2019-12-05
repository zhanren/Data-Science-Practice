# Conclusion, Reflection and Future Improvments
------------------------------------------------

In this study, I have compared three different strategies of collaborative filtering. In all three ML algothrims, the required the data structure are pretty simple; all we need is unique identifer of business (in this case restaurant), unique identifer of users and the ratings that the user gave to some of the businesses on the list. In the Implicit ALS, we need one extra step to approximate such rating to start with.

Thus, we can kind of see why collaborative filtering is a popular strategy to give recommendations for e-commerce or stream service company. The dataset up is really easy; the concept is straight foward and we have libraries ready for us to implement. The calculation steps are relatively easy to implement. No wonder it becomes with winning strategy for NetFlix competition. 

However, I do see a few problems with collaborative filtering in real world business scenario: It does require a ton of data point to start with. That is, we will need a respectful amount of users is using the service so that we can collect the data from them. In some cases, company could also be struggling to get customer write any reviews or give any rating. We see that a lot of companies give monetary incentives for customers to fill in these ratings. That could be too expensive for startups to afford. Even we can use a more flexible Implicit ALS, we still need to define the "arbitrary rating" for ourself and that "arbitrary rating" may or may not reflects the true feelings of a customer on a certain product.

And because of this problem, I would suggest that collaborative filtering would only be good for businesses like E-commerce involving consumer goods, Stream service, service suggestion apps (e.g. Yelp, Zomato), and social media platforms, because they are naturally in a better position of collecting user's data. For industries that lack of consumer facing opportunies, it would become difficult for them to use collaborative filtering to create their strategy.

Also, the fact that collaborative filtering only used rating to evlaute the business can be problematic; for example, a review today can be more indicitive about one's preference than a review two years ago. We can advanced collaborative filtering potentially by giving weights to each rating with time, usefullness in mind.


## What's Next
-------------------------------
I will be using Neural Network to clustering cell phones
