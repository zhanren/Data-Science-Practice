from pyspark.sql import SparkSession
from pyspark.ml.recommendation import ALS
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.sql.window import Window
from pyspark.sql.types import IntegerType
from pyspark.sql.functions import *
from pyspark.sql import Row
import time
import os
import matplotlib.pyplot as plt
import numpy as np
os.chdir("D:\\Yelp data")

spark = SparkSession \
        .builder \
        .appName("movie recommendation") \
        .getOrCreate()
sc=spark.sparkContext
sc.setCheckpointDir('C:\\Users\\qwerdf\\Desktop\\Coding\\pyspark')
#Add checkpoint becasue it is HDFS at a local machine; memory can be a contrainst in this case.

joint_table=spark.read.load("yelp_train.csv",format='csv',header=True)
#joint_table.show(10)

ALS_data=joint_table.withColumn("business_id_int",rank().over(Window.orderBy(asc("business_id")))) \
                    .withColumn("user_id_int",rank().over(Window.orderBy(asc("user_id")))) \
                    .withColumn("stars_review_int",joint_table["stars_review"].cast(IntegerType())) \
                    .select(["business_id_int","user_id_int","stars_review_int","name"]).cache()

ALS_data.createOrReplaceTempView("ALS_data")
#ALS_data.show(10)

train,validation=ALS_data.randomSplit([0.8,0.2],seed=1992)
train.createOrReplaceTempView("train")
spark.sql(
    "Select * \
     FROM  train \
     WHERE stars_review_int is null or business_id_int is null or user_id_int is null"
).show(10)

def find_restaurant_id(data,restaurant_list):
    """
    function to user restaurant name to find restaurant id
    
    --------------
    
    data: spark dataset that contains restaurant name, restaurant id combination
    
    restaurant_list: list, input list of restaurant name that needs to be transfer to restaurant id
    
    """
    final_list=[]
    if restaurant_list is None:
        return final_list
    for restaurant in restaurant_list:
        restaurant_id=data.where(col('name') \
                          .like(restaurant)) \
                          .select('business_id_int') \
                          .distinct() \
                          .rdd \
                          .map(lambda r:r[0]) \
                          .collect()    
                          
        final_list.extend(restaurant_id)
    return final_list
    
def add_new_user_data(train_data,my_fav,my_least_fav=None):
    """
    function to add new user's data into train model
    
    --------------
    
    
    parameters:
    
    train_data: spark dataframe, Initial data for user_id,business_id,rating combinations
    
    my_fav: list of strings, favourite restaurant list; Assume these restaurants are marked as 5
    
    my_least_fav: list of strings, least favourite restaurant list; Assume these restaurants are makred as 1
    """
    new_user_id=train_data.rdd.map(lambda r:r[1]).max()+1
    columns=['business_id_int','user_id_int','stars_review','name']
    print("initialize data for new userid {}".format(new_user_id))
    fav_list=find_restaurant_id(train_data,my_fav)
    fav_rows=[(restaurant_id,new_user_id,5,restaurant) for restaurant_id,restaurant in zip(fav_list,my_fav)]
    fav_df=spark.createDataFrame(fav_rows,columns)
    final_set=train_data.union(fav_df)
    if my_least_fav is not None:
        least_fav_list=find_restaurant_id(train_data,my_least_fav)
        least_fav_rows=[(restaurant_id,new_user_id,1,restaurant) for restaurant_id,restaurant in zip(least_fav_list,my_least_fav)]
        least_fav_df=spark.createDataFrame(least_fav_rows,columns)
        final_set=train_data.union(least_fav_df)
    return new_user_id,final_set
    
def find_personal_recommendation_als(train_data,my_fav,my_least_fav=None,reg_param=0.3,rank=16,maxiter=17):
    """
    function to give personal recommendations to the defined user who has record of favourite restaurant and least favourite restaurant
    
    -----------
    parameters:
    
    train_data: spark dataframe, Initial data for user_id,business_id,rating combinations
    
    my_fav: list of strings, favourite restaurant list; Assume these restaurants are marked as 5
    
    my_least_fav: list of strings, least favourite restaurant list; Assume these restaurants are makred as 1
    
    reg_param: lambda in ALS, defined the overfitting penalty of the ALS
    
    rank: rank of ALS, defined the complexity of ALS
    
    
    """
    best_regularization=reg_param
    best_rank=rank
    new_user_id,new_set=add_new_user_data(train_data,my_fav,my_least_fav)
    
    best_als=ALS(maxIter=maxiter, \
             regParam=best_regularization, \
             userCol="user_id_int", \
             itemCol="business_id_int", \
             ratingCol="stars_review_int", \
             rank=best_rank, \
             coldStartStrategy="drop", \
             checkpointInterval=2
             )
    model=best_als.fit(new_set)
    users=new_set.select(best_als.getUserCol()).where(col('user_id_int')==new_user_id)
    userSubsetRecs=model.recommendForUserSubset(users,10)
    print("Here are the top 10 recommandations for you given your favourite and least favourite food")
    for restaurant in userSubsetRecs.select("recommendations").collect()[0][0]:
        restaurant_id=restaurant.__getattr__("business_id_int")
        restaurant_name=train_data.where(col('business_id_int')==restaurant_id).select('name').distinct().collect()
        print(restaurant_name[0].__getattr__("name"))
    return userSubsetRecs


#test case
#my_fav=['Emerald Chinese Restaurant']
#find_personal_recommendation_als(ALS_data,my_fav)
#my_fav=["J's Fish & Chips"]
#find_personal_recommendation_als(ALS_data,my_fav)
