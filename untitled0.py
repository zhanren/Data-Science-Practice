# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 19:22:02 2019

@author: qwerdf
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 19:04:00 2019

@author: qwerdf
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Nov 29 15:26:03 2019

@author: qwerdf
"""

from pyspark.sql import SparkSession
from pyspark.ml.recommendation import ALS
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.sql.window import Window
from pyspark.sql.types import IntegerType
from pyspark.sql.functions import *
import time
import os
os.chdir("D:\\Yelp data") 


spark = SparkSession \
        .builder \
        .appName("movie recommendation") \
        .getOrCreate()
sc=spark.sparkContext
sc.setCheckpointDir('C:\\Users\\qwerdf\\Desktop\\Coding\\pyspark')
base_spark_table=spark.read.load("Ontario_restaurant.csv",format='csv',header=True)
joint_table=spark.read.load("yelp_train.csv",format='csv',header=True)

ALS_data=joint_table.withColumn("business_id_int",rank().over(Window.orderBy(asc("business_id")))) \
                    .withColumn("user_id_int",rank().over(Window.orderBy(asc("user_id")))) \
                    .withColumn("stars_review_int",joint_table["stars_review"].cast(IntegerType())) \
                    .select(["business_id_int","user_id_int","stars_review_int","name"]).cache()

ALS_data.createOrReplaceTempView("ALS_data")
ALS_data.show(10)




train,validation=ALS_data.randomSplit([0.8,0.2],seed=1992)
train.createOrReplaceTempView("train")
spark.sql(
    "Select * \
     FROM  train \
     WHERE stars_review_int is null"
).show(10)

def ALS_parameter_tuning(train_data,validation_data,maxiter,reg_param,rank):
        min_error=float('inf')
        best_rank=-1
        best_regularization=0,
        best_model=None
        run_time=time.time()
        for rank_iter in ranks:
            for reg in reg_param:
                start_time=time.time()
                als=ALS(
                        maxIter=maxiter,
                        regParam=reg,
                        userCol="user_id_int",
                        itemCol="business_id_int",
                        ratingCol="stars_review_int",
                        rank=rank_iter,
                        coldStartStrategy="drop",
                        checkpointInterval=2
                        )
                model=als.fit(train_data)
                predictions=model.transform(validation_data)
                evaluator=RegressionEvaluator(metricName="rmse",labelCol="stars_review_int",
                                              predictionCol="prediction")
                rmse=evaluator.evaluate(predictions)
                print("With reg Param={} and rank={}, RMSE of ALS is {}".format(reg,rank_iter,rmse))
        if rmse<=min_error:
            min_error=rmse
            best_rank=rank_iter
            best_regularization=reg
            best_model=model
        run_time=time.time()-run_time
        return best_rank,best_regularization,best_model,run_time
         
maxiter=10
ranks=range(10,21,2)
start_time = time.time()
reg_params=[0.02,0.05,0.1,0.2,0.3,0.5]

best_rank,best_regularization,best_model,run_time=ALS_parameter_tuning(train_data=train,validation_data=validation,maxiter=maxiter,reg_param=reg_params,rank=ranks)
#best_rank=20,best_regularization=0.5

def find_restaurant_id(data,restaurant_list):
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

#test find_restaurant_id(ALS_data,['Emerald Chinese Restaurant'])

def add_new_user_data(train_data,my_fav,sc=sc,my_least_fav=None):
    
    new_user_id=ALS_data.rdd.map(lambda r:r[1]).max()+1
    print("initialize data for new userid {}".format(new_user_id))
    fav_list=find_restaurant_id(train_data,my_fav)
    fav_rows=[{restaurant_id,new_user_id,5,restaurant} for restaurant_id,restaurant in zip(fav_list,my_fav)]
    fav_rdd=sc.parallelize(fav_rows)
    final_set=train_data.rdd.union(fav_rdd)
    if my_least_fav is not None:
        least_fav_list=find_restaurant_id(train_data,my_least_fav)
        least_fav_rows=[{restaurant_id,new_user_id,1,restaurant} for restaurant_id,restaurant in zip(least_fav_list,my_least_fav)]
        least_fav_rdd=sc.parallelize(least_fav_rows)
        final_set=final_set.union(least_fav_rdd)
    return final_set
    
#test add_new_user_data(train_data=ALS_data,my_fav=['Emerald Chinese Restaurant'])
    
    
    

def find_person_recommandation_als():
    
    best_als=ALS(maxIter=maxiter, \
             regParam=best_regularization, \
             userCol="user_id_int", \
             itemCol="business_id_int", \
             ratingCol="stars_review_int", \
             rank=best_rank, \
             coldStartStrategy="drop", \
             checkpointInterval=2
             )

    users=ALS_data.select(best_als.getUserCol()).distinct().limit(3)
    userSubsetRecs=best_model.recommendForUserSubset(users,10)
    
