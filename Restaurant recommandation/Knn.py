import pandas as pd
import os
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors

os.chdir("D:\Yelp data")
yelp_business=pd.read_json("business.json",lines=True)
review=pd.read_csv("yelp_review.csv")
user=pd.read_csv("yelp_user.csv")

Ontario_restaurant=yelp_business[yelp_business.categories.str.contains("Restaurant")==1][yelp_business["state"]=="ON"]
Ontario_restaurant=Ontario_restaurant[["business_id","categories","city","name","postal_code","review_count","stars"]]
Ontario_restaurant=Ontario_restaurant.set_index("business_id")

final_dataset=review.join(Ontario_restaurant,how="inner",on="business_id",lsuffix="_review",rsuffix="_business")
final_dataset=final_dataset.join(user.set_index("user_id"),how="inner",on="user_id",lsuffix="_final",rsuffix="_user")

final_dataset.groupby("stars_review").count()["user_id"].plot(kind="bar")
avg_rating=final_dataset["stars_review"].mean()
print("Average rating for restaurant in Ontario is {}".format(round(avg_rating,2)))

final_dataset.groupby("business_id").agg({"stars_review":"mean"}).hist(bins=20)


review_count=pd.DataFrame(final_dataset.groupby("user_id",as_index=False).size(),columns=["count"]).sort_values("count",ascending=False)

pd.DataFrame.hist(review_count,bins=100)

Ontario_restaurant_mat=final_dataset.pivot(index="business_id",columns="user_id",values="stars_review").fillna(0)

def knn_model():
    model=NearestNeighbors(metric="cosine",algorithm="brute",n_neighbors=20,n_jobs=-1)
    return model
model=knn_model()


def knn_recommandation(data,fav_restaurant,n_recommendations=10,weighted=False):
    """
    using yelp data to recommand restaurant
    
    knn_approach

    Parameters
    ----------
    model_knn: sklearn model, knn model

    data: yelp restaurant data converted to matrix:
          row as business identifier
          column as user identifier

    input: favorite restaurant

    n_recommendations: int, top n recommendations
    """
    if 'model' in globals():
        global model
    else:
        model=knn_model()
    # fit
    model.fit(data)
    print("Find restaurants similar to {} based on user input".format(fav_restaurant))
    # inference
    print('Here are the top ten recommandations:')
    print('......\n')
    business_id=Ontario_restaurant[Ontario_restaurant["name"]==fav_restaurant].index[0]
    distances, indices = model.kneighbors(data.filter(like=business_id,axis='index'), n_neighbors=n_recommendations+1)
    # get list of raw idx of recommendations
    raw_recommends = \
        sorted(list(zip(indices.squeeze().tolist(), distances.squeeze().tolist())), key=lambda x: x[1])[:0:-1]
    # print recommendations
    print('Recommendations for {}:'.format(my_favorite))
    for i, (idx, dist) in enumerate(raw_recommends):
        print('{0}: {1}, with distance of {2}'.format(i+1,list(Ontario_restaurant["name"][Ontario_restaurant.index==Ontario_restaurant_mat.index[idx]])[0], dist))


#test
"""        
my_favorite = 'Emerald Chinese Restaurant'

knn_recommandation(
    data=Ontario_restaurant_mat,
    fav_restaurant=my_favorite)
    
my_favorite = "J's Fish & Chips"


knn_recommandation(
    data=Ontario_restaurant_mat,
    fav_restaurant=my_favorite)
"""
