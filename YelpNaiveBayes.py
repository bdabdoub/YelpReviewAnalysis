# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 20:08:40 2017

@author: Bradley Dabdoub
"""
import sys
import gc
import time
import numpy
import pandas
from sklearn.cross_validation import train_test_split 
from collections import Counter
import re
from sklearn.metrics import f1_score
from sklearn.metrics import accuracy_score
from sklearn import metrics
import math

start = time.clock()
#IMPORTANT: Change nrows paramater to determine how many data samples you want in your whole set (or remove it for entire dataset)
df = pandas.read_csv('processed-reviews-ratings.csv', nrows=8000, header=0, delimiter=',', usecols=["text", "stars"])#,encoding ='latin1'
df = df.dropna(how='any', axis=0)

#Select column 3, "text", store in reviews
reviews = df.iloc[:, 0].values

#Select column 5, "stars", store in ratings
ratings = df.iloc[:, 1].values

#Train test split with random state 1, maintain proportion of labels in Y_sample, train/test_validation are 14/6% of original data
X_train, X_test_validation, Y_train, Y_test_validation, = train_test_split(reviews, ratings, test_size=.3, stratify=ratings, random_state=1)

#Train test split with random state 1, maintain proportion of labels in Y_test_validation, validation/test are 3/3% of original data
X_validation, X_test, Y_validation, Y_test = train_test_split(X_test_validation, Y_test_validation, test_size= .5, stratify=Y_test_validation, random_state=1)

stopwords = {'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', 'aren\'t', 'as', 'at', 'be',
'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', 'can\'t', 'cannot', 'could', 'couldn\'t', 'did', 'didn\'t',
'do', 'does', 'doesn\'t', 'doing', 'don\'t', 'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had', 'hadn\'t', 'has' 'hasn\'t',
'have', 'haven\'t', 'having', 'he', 'he\'d', 'he\'ll', 'he\'s', 'her', 'here', 'here\'s', 'hers', 'herself', 'him', 'himself', 'his', 'how',
'how\'s', 'i', 'i\'d', 'i\'ll', 'i\'m', 'i\'ve', 'if', 'in', 'into', 'is', 'isn\'t', 'it', 'it\'s', 'its', 'itself', 'let\'s', 'me', 'more',
'most', 'mustn\'t', 'my', 'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'ought', 'our', 'ours', 'ourselves',
'out', 'over', 'own', 'same', 'shan\'t', 'she', 'she\'d', 'she\'ll', 'she\'s', 'should', 'shouldn\'t', 'so', 'some', 'such', 'than',
'that', 'that\'s', 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', 'there\'s', 'these', 'they', 'they\'d', 'they\'ll',
'they\'re', 'they\'ve', 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', 'wasn\'t', 'we', 'we\'d', 'we\'ll',
'we\'re', 'we\'ve', 'were', 'weren\'t', 'what', 'what\'s', 'when', 'when\'s', 'where', 'where\'s', 'which', 'while', 'who', 'who\'s',
'whom', 'why', 'why\'s', 'with', 'won\'t', 'would', 'wouldn\'t', 'you', 'you\'d', 'you\'ll', 'you\'re', 'you\'ve', 'your', 'yours',
'yourself', 'yourselves', ',', '.', '-', '!'}


def bagOWords(reviews, labels, target):
    wordList = []
    for index,review in enumerate(reviews):
        if (labels[index] == target):
            reviewWords = review.split() 
            for reviewWord in reviewWords:
                wordList.append(reviewWord)
    return wordList

oneStarBag = bagOWords(X_train, Y_train, 1)
twoStarBag = bagOWords(X_train, Y_train, 2)
threeStarBag = bagOWords(X_train, Y_train, 3)
fourStarBag = bagOWords(X_train, Y_train, 4)
fiveStarBag = bagOWords(X_train, Y_train, 5)

oneStarCounter = Counter(x for x in oneStarBag if x not in stopwords)
twoStarCounter = Counter(x for x in twoStarBag if x not in stopwords)
threeStarCounter = Counter(x for x in threeStarBag if x not in stopwords)
fourStarCounter = Counter(x for x in fourStarBag if x not in stopwords)
fiveStarCounter = Counter(x for x in fiveStarBag if x not in stopwords)

oneStarCounter = {k:oneStarCounter[k] for k in oneStarCounter if oneStarCounter[k] > 1}
twoStarCounter = {k:twoStarCounter[k] for k in twoStarCounter if twoStarCounter[k] > 1}
threeStarCounter = {k:threeStarCounter[k] for k in threeStarCounter if threeStarCounter[k] > 1}
fourStarCounter = {k:fourStarCounter[k] for k in fourStarCounter if fourStarCounter[k] > 5}
fiveStarCounter = {k:fiveStarCounter[k] for k in fiveStarCounter if fiveStarCounter[k] > 5}

labelCount = Counter(Y_train)

oneStarCount = labelCount.get(1)
twoStarCount = labelCount.get(2)
threeStarCount = labelCount.get(3)
fourStarCount = labelCount.get(4)
fiveStarCount = labelCount.get(5)

total = (oneStarCount + twoStarCount + threeStarCount + fourStarCount + fiveStarCount) 

oneStarClassProb = oneStarCount / total
twoStarClassProb = twoStarCount / total
threeStarClassProb = threeStarCount / total
fourStarClassProb = fourStarCount / total
fiveStarClassProb = fiveStarCount / total

def NaiveBayes(review, count, prob):
    pred = 1
    logProb = math.log(prob)
    reviewWords = Counter(re.split("\s+", review))

    for reviewWord in reviewWords:
        # print(pred *(reviewWords.get(reviewWord) * ((count.get(reviewWord, 0) + 1) / sum(count.values()))))
        pred += math.log(reviewWords.get(reviewWord) * ((count.get(reviewWord, 0) + 1) / sum(count.values())))
        # pred *= math.log(reviewWords.get(reviewWord) * ((count.get(reviewWord, 0) + 1) / sum(count.values())))
        if(pred == 0.0):
            sys.exit(0)
    
    pred += prob
    return pred  

def predict(review):  
    oneStarPrediction = NaiveBayes(review, oneStarCounter, oneStarClassProb)
    twoStarPrediction = NaiveBayes(review, twoStarCounter, twoStarClassProb)
    threeStarPrediction = NaiveBayes(review, threeStarCounter, threeStarClassProb)
    fourStarPrediction = NaiveBayes(review, fourStarCounter, fourStarClassProb)
    fiveStarPrediction = NaiveBayes(review, fiveStarCounter, fiveStarClassProb)
    
    classPredictions = {}
    classPredictions[1] = oneStarPrediction
    classPredictions[2] = twoStarPrediction
    classPredictions[3] = threeStarPrediction
    classPredictions[4] = fourStarPrediction
    classPredictions[5] = fiveStarPrediction
    
    #return the key whose value is the max of all the values, where 1=<key=<5, the most likely star rating
    predictedStarRating = max(classPredictions, key=classPredictions.get)

    
    #there should never be a probability of 0.0
    if(classPredictions[predictedStarRating] == 0.0):
        print("Error: classPredictions[predictedStarRating] == 0.0")
        sys.exit(0)
    return predictedStarRating


def main():
    predictions = []
    count = 0
    for review in X_validation:
        count = count +1
        
        predictions.append(predict(review))
    end = time.clock()
    duration = end - start
    print("Total Reviews:", count)

    misclass = numpy.where(Y_validation != predictions, 1, 0)
    print(metrics.classification_report(Y_validation, predictions, target_names=["1", "2", "3", "4", "5"]))

    print('Misclassified samples: %d' % misclass.sum())
    print('Accuracy: %.2f' % accuracy_score(Y_validation, predictions))
    print('F1 Score: ' +  str(f1_score(Y_validation, predictions, average=None)))
    print("---Duration: %s seconds ---" % duration)
    gc.collect()

main()





            
    





















