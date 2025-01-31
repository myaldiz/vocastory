# <mark style="color:gray;font-size:35px;font-family:courier;">voca</mark><mark style="color:blue;font-weight:bold;font-family:courier;background:#dbdbdb;font-size:35px">story</mark>

## Problem Statement
- People struggle to memorise words effectively while learning a new language or preparing for an exam. Existing systems mostly rely on repetition without  letting users actively put the words they learn into a context

## Our Solution
- A website that enables collaborative storytelling to memorise the words in a list. 

## How to RUN the website
- Please read the mystory/README.md

## Guide to repository structure
- Enter the mystory directory. Inside you will see the following folders:
    - ./vocastory contains views.py and models.py which are the most IMPORTANT files
    - ./templates contains html files
    - ./static contains stylesheets and js files
    - ./mystory contains settings file that mentions dependencies and database
    - ./accounts helps manage users
    - ./fixtures contains the json files with pre-existing data to partially fill the website
    
## Tasks

- We have three different modes in the game explained below as tasks:
    - Task 1 (Write): Write a sentence by using a word from the word list, with the intent of continuing the story
        - This feature is called ``writer's mode``
        - Multiple responses collected from different users.
    - Task 2 (Pick): Choose the best sentence (creative+fits in with the previous ones)
        - This feature is called ``reader's mode``
        - Winner will be selected as a next sentence to continue the story.
        - Next, users switch back to writing mode to continue the story. (Exact mechanism will be selected by user study in the future)
    - Task 3 (Review): Review and grade the story as a whole based on the provided criteria (creativity, coherence, fun)
        - This feature is called ``reviewer's mode``


## Prototype
* [Link](https://invis.io/UKUQEFBZMXH) to the low-fi prototype
