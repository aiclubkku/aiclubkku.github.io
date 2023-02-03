# -*- coding: utf-8 -*-
"""TensorFlow-chatbot.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/182gGKoVtowAkPSkB2CY9_hsyJz_dvX83

# **Downloading NLTK**
"""

nltk.download('all')

"""# **Importing libraries and initializing json and lemmatizer**"""

import random
import json
import pickle
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
import tensorflow as tf

data = json.loads(open('/content/intents.json').read())

lemmatizer = WordNetLemmatizer()

"""# **Preprocessing data**"""

# words is the list of our vocabulary with each word appearing only once from our sentence
# classes are the labels associated with the particular pattern
# documents is a list of [patterns, tag]
# ignore letters is used for cleaning input data
words, classes, documents, ignore_letters = [], [], [], ['?','.',',',"'", '!']

# we need to convert our patterns (X) and tags (y) in numerical value so that the machine can read it
for intent in data['intents']:
  for pattern in intent['patterns']:
    # word_tokenize will convert 'how are you' to ['how', 'are', 'you']
    word_list = nltk.word_tokenize(pattern)
    words.extend(word_list)
    # your document will look like this (['how', 'are', 'you'], 'greetings')
    documents.append((word_list, intent['tags']))
    if intent['tags'] not in classes:
      classes.append(intent['tags'])

# over here we are creating our vocabulary where each word has its own space and identitiy suppose 'hello' will have [0,0,0,1,0,0] and 
# 'goodbye' will have [0,1,0,0,0,0] and so on...
# sort will put everything in ascending order and set will delete and repeated value
words = sorted(set([lemmatizer.lemmatize(word.lower()) for word in words if word not in ignore_letters]))
classes = sorted(set(classes))

# training is a similar list like documents except that everything in it is in form of 0's and 1's like ([0,0,0,1,0,0,0], [0,1,0])0
training = []
for document in documents: 
  # output list is for our classes / labels / tags
  output = [0 for _ in range(len(classes))]
  # bag is for converting sentences into 0 and 1 matrices
  bag = []
  # reading the patterns from documents [(['how', 'are', 'you'], 'greetings')]
  # where document = (['how', 'are', 'you'], 'greetings')
  # and document[0] = ['how', 'are', 'you']
  word_patterns = document[0]
  word_patterns = [lemmatizer.lemmatize(w.lower()) for w in word_patterns]
  # looping through the vocabulary we created and converting 0 to 1 where the word_pattern matches the word from our vocabulary
  for word in words:
    bag.append(1) if word in word_patterns else bag.append(0)
  output[classes.index(document[1])] = 1
  training.append([bag, output])

random.shuffle(training)
training = np.array(training, dtype='object')

train_x = list(training[:, 0])
train_y = list(training[:, 1])

"""# **Building Neural Network**"""

# Dense is a normal layer
# dropout layer helps model from overfitting or underfitting
model = tf.keras.Sequential([
    tf.keras.layers.Dense(128, input_shape=(len(train_x[0]),), activation='relu'),
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dropout(0.5),
    # since we only have 3 tags for now, softmax gives output as 0.2, 0.7, 0.1 meaning the second tag has highest probability 
    tf.keras.layers.Dense(len(train_y[0]), activation='softmax')
])

model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

model.fit(train_x, train_y, epochs=200)

"""# **Program to use the model**"""

def clean_sentence(sentence):
  sentence_words = nltk.word_tokenize(sentence)
  sentence_words = [lemmatizer.lemmatize(w) for w in sentence_words]
  return sentence_words

def convert_bagofwords(sentence):
  sentence_words = clean_sentence(sentence)
  bag = [0 for _ in range(len(words))]

  for w in sentence_words:
    for i, word in enumerate(words):
      if word == w:
        bag[i] = 1
  return np.array(bag)

def predict_class(sentence):
  bagofwords = convert_bagofwords(sentence)
  result = model.predict(np.array([bagofwords]))[0]
  ERROR_THRESHOLD = 0.25
  final_result = [[index, result] for index, result in enumerate(result) if result > ERROR_THRESHOLD]
  final_result.sort(reverse=True)
  return_list = []
  for r in final_result:
    return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})
  return return_list

def get_response(intents_list, intents_json):
  tag = intents_list[0]['intent']
  list_of_intents = intents_json['intents']
  for i in list_of_intents:
    if i['tags'] == tag:
      result = random.choice(i['responses'])
      break
  return result

"""# **Talk to the chatbot**"""

end = False
while end != True:
  ui = input("Type here: ")
  if ui == "stop":
    break
  else:
    intentsofui = predict_class(ui)
    respond = get_response(intentsofui, data)
    print(respond)