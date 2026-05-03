# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
"""
GapLens — Question Seeder
Seeds 20 questions each for: Python, Java, C++, C, JavaScript, Data Science, System Design
Run: python seed_questions.py
"""
import requests, html, time, random
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['gaplens']
col = db['questions']

# ── Hardcoded questions ─────────────────────────────────────────────────────

QUESTIONS = {
"Python": [
  {"question":"What is the output of print(type([]))?","options":["<class 'list'>","<class 'array'>","<class 'tuple'>","Error"],"answer":"<class 'list'>"},
  {"question":"Which keyword is used to define a function in Python?","options":["func","def","function","lambda"],"answer":"def"},
  {"question":"What does 'len([1,2,3])' return?","options":["3","2","4","Error"],"answer":"3"},
  {"question":"Which of these is a mutable data type in Python?","options":["tuple","str","list","int"],"answer":"list"},
  {"question":"What is the result of 3 ** 2 in Python?","options":["6","9","8","5"],"answer":"9"},
  {"question":"Which module is used for regular expressions in Python?","options":["regex","re","regexp","rx"],"answer":"re"},
  {"question":"What does 'pass' do in Python?","options":["Exits a loop","Does nothing","Skips a value","Raises error"],"answer":"Does nothing"},
  {"question":"What is the output of bool('')?","options":["True","False","None","Error"],"answer":"False"},
  {"question":"Which method removes the last item of a list?","options":["remove()","delete()","pop()","discard()"],"answer":"pop()"},
  {"question":"What is the correct way to create a dictionary?","options":["{key:val}","[key:val]","(key:val)","<key:val>"],"answer":"{key:val}"},
  {"question":"What does 'self' refer to in a class method?","options":["The class","The parent class","The instance","A global variable"],"answer":"The instance"},
  {"question":"Which built-in function returns the largest item?","options":["largest()","max()","top()","high()"],"answer":"max()"},
  {"question":"What does 'enumerate()' return?","options":["A list","A dict","An enumerate object","A tuple"],"answer":"An enumerate object"},
  {"question":"How do you open a file in Python?","options":["open()","file()","read()","load()"],"answer":"open()"},
  {"question":"What is the output of [1,2,3][::-1]?","options":["[3,2,1]","[1,2,3]","[2,3,1]","Error"],"answer":"[3,2,1]"},
  {"question":"Which of these is NOT a Python data type?","options":["int","float","char","str"],"answer":"char"},
  {"question":"What is a lambda function?","options":["A named function","An anonymous function","A class method","A module"],"answer":"An anonymous function"},
  {"question":"What does 'import os' do?","options":["Imports operating system module","Creates OS","Deletes OS","None"],"answer":"Imports operating system module"},
  {"question":"What is the output of 10//3?","options":["3.33","3","4","Error"],"answer":"3"},
  {"question":"Which decorator makes a method a static method?","options":["@static","@classmethod","@staticmethod","@method"],"answer":"@staticmethod"},
],
"Java": [
  {"question":"What is the size of int in Java?","options":["8 bits","16 bits","32 bits","64 bits"],"answer":"32 bits"},
  {"question":"Which keyword creates a class object?","options":["create","new","make","build"],"answer":"new"},
  {"question":"What does JVM stand for?","options":["Java Virtual Memory","Java Variable Machine","Java Virtual Machine","Java Version Manager"],"answer":"Java Virtual Machine"},
  {"question":"Which method is the entry point of a Java program?","options":["start()","main()","run()","init()"],"answer":"main()"},
  {"question":"Which of these is NOT a Java primitive type?","options":["int","String","char","boolean"],"answer":"String"},
  {"question":"What does 'final' keyword do?","options":["Makes variable mutable","Makes variable constant","Deletes variable","None"],"answer":"Makes variable constant"},
  {"question":"Which exception handles division by zero?","options":["NullPointerException","ArithmeticException","IndexOutOfBoundsException","ClassCastException"],"answer":"ArithmeticException"},
  {"question":"Which interface allows iteration in Java?","options":["Iterable","Iterator","Collection","List"],"answer":"Iterable"},
  {"question":"What is the default value of a boolean in Java?","options":["true","false","null","0"],"answer":"false"},
  {"question":"Which keyword is used for inheritance?","options":["implements","inherits","extends","super"],"answer":"extends"},
  {"question":"What is autoboxing?","options":["Converting primitive to wrapper class","Converting class to primitive","String to int","Array to list"],"answer":"Converting primitive to wrapper class"},
  {"question":"Which collection maintains insertion order?","options":["HashSet","TreeSet","LinkedHashMap","HashMap"],"answer":"LinkedHashMap"},
  {"question":"What does 'static' mean?","options":["Belongs to instance","Belongs to class","Private method","Abstract"],"answer":"Belongs to class"},
  {"question":"Which keyword prevents a class from being subclassed?","options":["static","abstract","final","sealed"],"answer":"final"},
  {"question":"What is polymorphism?","options":["One class, many methods","Same method name, different behaviour","Multiple inheritance","Encapsulation"],"answer":"Same method name, different behaviour"},
  {"question":"Which Java version introduced lambdas?","options":["Java 6","Java 7","Java 8","Java 11"],"answer":"Java 8"},
  {"question":"What is the parent class of all Java classes?","options":["Base","Root","Object","Super"],"answer":"Object"},
  {"question":"Which operator is used for string concatenation?","options":["+","&","||",".."],"answer":"+"},
  {"question":"What does 'this' refer to?","options":["Parent class","Current class instance","Static field","Interface"],"answer":"Current class instance"},
  {"question":"Which access modifier is visible only within the class?","options":["public","protected","private","default"],"answer":"private"},
],
"C++": [
  {"question":"Which operator is used for dynamic memory allocation?","options":["malloc","new","alloc","create"],"answer":"new"},
  {"question":"What is a destructor?","options":["Allocates memory","Frees memory automatically","Creates an object","Copies an object"],"answer":"Frees memory automatically"},
  {"question":"Which of these is a valid C++ reference declaration?","options":["int *x=&a","int &x=a","int x=&a","int #x=a"],"answer":"int &x=a"},
  {"question":"What does 'virtual' keyword enable?","options":["Multiple inheritance","Runtime polymorphism","Templates","Operator overloading"],"answer":"Runtime polymorphism"},
  {"question":"What is the scope resolution operator?","options":["->","::","..","**"],"answer":"::"},
  {"question":"Which header is required for cout?","options":["<stdio.h>","<iostream>","<conio.h>","<output.h>"],"answer":"<iostream>"},
  {"question":"What is a template in C++?","options":["A class design","Generic programming","A destructor","An interface"],"answer":"Generic programming"},
  {"question":"What does STL stand for?","options":["Standard Template Library","Static Type Library","Standard Type Linker","None"],"answer":"Standard Template Library"},
  {"question":"Which of these is NOT a C++ access specifier?","options":["public","private","protected","internal"],"answer":"internal"},
  {"question":"What is operator overloading?","options":["Creating new operators","Redefining operator behaviour","Inheriting operators","None"],"answer":"Redefining operator behaviour"},
  {"question":"What is the output of sizeof(char)?","options":["2","4","1","8"],"answer":"1"},
  {"question":"What is a friend function?","options":["A global function","Can access private members","A virtual function","A static function"],"answer":"Can access private members"},
  {"question":"Which smart pointer has exclusive ownership?","options":["shared_ptr","weak_ptr","unique_ptr","auto_ptr"],"answer":"unique_ptr"},
  {"question":"What does 'inline' do?","options":["Includes a header","Suggests compiler to expand inline","Creates a loop","None"],"answer":"Suggests compiler to expand inline"},
  {"question":"Which loop is guaranteed to execute at least once?","options":["for","while","do-while","foreach"],"answer":"do-while"},
  {"question":"What is a pure virtual function?","options":["Has no body","Has a body","Is static","Is private"],"answer":"Has no body"},
  {"question":"Which container gives O(1) access by index?","options":["list","map","vector","set"],"answer":"vector"},
  {"question":"What is the use of 'nullptr' in C++11?","options":["Null character","Null pointer constant","Empty string","Zero"],"answer":"Null pointer constant"},
  {"question":"What is copy constructor?","options":["Creates object from scratch","Creates object from existing object","Destroys object","Moves object"],"answer":"Creates object from existing object"},
  {"question":"Which C++ keyword avoids name conflicts?","options":["class","namespace","struct","union"],"answer":"namespace"},
],
"C": [
  {"question":"Which function is used to print output in C?","options":["print()","echo()","printf()","cout"],"answer":"printf()"},
  {"question":"What does '&' operator return?","options":["Value","Address","Size","Pointer"],"answer":"Address"},
  {"question":"Which header is required for malloc()?","options":["<string.h>","<math.h>","<stdlib.h>","<stdio.h>"],"answer":"<stdlib.h>"},
  {"question":"What is a pointer?","options":["A data type","Variable that stores address","A function","An array"],"answer":"Variable that stores address"},
  {"question":"Which keyword is used to define constants?","options":["constant","final","const","#define only"],"answer":"const"},
  {"question":"What is the return type of main() in C?","options":["void","int","char","float"],"answer":"int"},
  {"question":"What does 'sizeof' operator return?","options":["Value","Number of elements","Size in bytes","Pointer"],"answer":"Size in bytes"},
  {"question":"Which loop has no guaranteed minimum execution?","options":["do-while","for","while","Both for and while"],"answer":"Both for and while"},
  {"question":"What is a structure in C?","options":["A function","User-defined data type","A pointer","An array"],"answer":"User-defined data type"},
  {"question":"Which function copies strings?","options":["strcopy()","strdup()","strcpy()","copy()"],"answer":"strcpy()"},
  {"question":"What is the correct way to declare a pointer?","options":["int p","int &p","int *p","int #p"],"answer":"int *p"},
  {"question":"Which storage class limits scope to file?","options":["auto","register","extern","static"],"answer":"static"},
  {"question":"What is a segmentation fault?","options":["Syntax error","Invalid memory access","Overflow","File not found"],"answer":"Invalid memory access"},
  {"question":"What does fclose() do?","options":["Opens file","Reads file","Closes file","Deletes file"],"answer":"Closes file"},
  {"question":"What is the output of printf(\"%d\", 5/2)?","options":["2.5","2","3","Error"],"answer":"2"},
  {"question":"Which keyword transfers control unconditionally?","options":["break","continue","return","goto"],"answer":"goto"},
  {"question":"What is an array in C?","options":["Dynamic collection","Fixed-size collection of same type","Linked list","Pointer"],"answer":"Fixed-size collection of same type"},
  {"question":"Which function gets input from user?","options":["input()","get()","scanf()","read()"],"answer":"scanf()"},
  {"question":"What does 'void' mean as return type?","options":["Returns 0","Returns nothing","Returns null","Error"],"answer":"Returns nothing"},
  {"question":"Which operator is used to access struct members via pointer?","options":[".","->","*","&"],"answer":"->"},
],
"JavaScript": [
  {"question":"Which keyword declares a block-scoped variable?","options":["var","let","const","both let and const"],"answer":"both let and const"},
  {"question":"What does 'typeof null' return?","options":["null","undefined","object","boolean"],"answer":"object"},
  {"question":"Which method converts JSON string to object?","options":["JSON.stringify()","JSON.parse()","JSON.convert()","JSON.objectify()"],"answer":"JSON.parse()"},
  {"question":"What is a closure?","options":["A loop","Function + its lexical scope","A class","A module"],"answer":"Function + its lexical scope"},
  {"question":"What does '===' check?","options":["Value only","Type only","Value and type","Reference"],"answer":"Value and type"},
  {"question":"Which method adds element to end of array?","options":["push()","pop()","shift()","unshift()"],"answer":"push()"},
  {"question":"What is the event loop?","options":["A for loop","Mechanism for async code","A timer","A DOM event"],"answer":"Mechanism for async code"},
  {"question":"Which of these is NOT a JS primitive?","options":["string","number","object","boolean"],"answer":"object"},
  {"question":"What does 'async/await' do?","options":["Parallel execution","Synchronous-style async code","Creates a thread","Blocks code"],"answer":"Synchronous-style async code"},
  {"question":"Which method removes last array element?","options":["push()","pop()","shift()","splice()"],"answer":"pop()"},
  {"question":"What is 'NaN'?","options":["Not a Number","Null and None","New array notation","None"],"answer":"Not a Number"},
  {"question":"Which JS engine powers Chrome?","options":["SpiderMonkey","V8","Chakra","Hermes"],"answer":"V8"},
  {"question":"What does 'Promise.all()' do?","options":["Runs promises sequentially","Runs all promises in parallel","Returns first resolved","Cancels promises"],"answer":"Runs all promises in parallel"},
  {"question":"What is hoisting?","options":["Moving declarations to top","Removing variables","Async execution","Scope chaining"],"answer":"Moving declarations to top"},
  {"question":"Which method creates a shallow copy of array?","options":["copy()","clone()","slice()","splice()"],"answer":"slice()"},
  {"question":"What is prototype chain?","options":["Inheritance mechanism","A design pattern","A promise chain","A module system"],"answer":"Inheritance mechanism"},
  {"question":"Which operator spreads array elements?","options":["*","...",">>","&&"],"answer":"..."},
  {"question":"What does 'use strict' do?","options":["Enables strict mode","Locks variables","Compresses code","None"],"answer":"Enables strict mode"},
  {"question":"What is the DOM?","options":["Database Object Model","Document Object Model","Data Object Management","None"],"answer":"Document Object Model"},
  {"question":"Which built-in method sorts array?","options":["order()","sort()","arrange()","rank()"],"answer":"sort()"},
],
"Data Science": [
  {"question":"What does EDA stand for?","options":["Extensive Data Analysis","Exploratory Data Analysis","External Data API","None"],"answer":"Exploratory Data Analysis"},
  {"question":"Which library is used for data manipulation in Python?","options":["NumPy","Matplotlib","Pandas","Seaborn"],"answer":"Pandas"},
  {"question":"What is overfitting?","options":["Model performs well on training, poor on test","Model underfits data","Model ignores features","None"],"answer":"Model performs well on training, poor on test"},
  {"question":"What does NaN represent?","options":["Not a Number","Null and None","New array","None"],"answer":"Not a Number"},
  {"question":"Which algorithm is used for classification?","options":["Linear Regression","K-Means","Decision Tree","PCA"],"answer":"Decision Tree"},
  {"question":"What is a feature in ML?","options":["Label","Input variable","Output","Target"],"answer":"Input variable"},
  {"question":"What does correlation measure?","options":["Causation","Relationship between variables","Data spread","Missing values"],"answer":"Relationship between variables"},
  {"question":"Which metric is used for classification accuracy?","options":["RMSE","R-squared","F1 Score","MAE"],"answer":"F1 Score"},
  {"question":"What is the purpose of train-test split?","options":["To reduce dataset size","To evaluate model generalization","To remove outliers","None"],"answer":"To evaluate model generalization"},
  {"question":"What does K-Means do?","options":["Classifies labeled data","Clusters unlabeled data","Predicts continuous values","Reduces dimensions"],"answer":"Clusters unlabeled data"},
  {"question":"What is PCA used for?","options":["Classification","Dimensionality reduction","Clustering","Feature engineering"],"answer":"Dimensionality reduction"},
  {"question":"What is a confusion matrix?","options":["Error in logic","Table of predictions vs actual","A type of chart","A loss function"],"answer":"Table of predictions vs actual"},
  {"question":"Which is a supervised learning algorithm?","options":["K-Means","DBSCAN","SVM","Apriori"],"answer":"SVM"},
  {"question":"What does RMSE measure?","options":["Classification error","Regression error magnitude","Correlation","Data skewness"],"answer":"Regression error magnitude"},
  {"question":"What is normalisation?","options":["Scaling data to 0-1 range","Removing nulls","Encoding categories","None"],"answer":"Scaling data to 0-1 range"},
  {"question":"Which library creates visualisations?","options":["Pandas","NumPy","Matplotlib","Scikit-learn"],"answer":"Matplotlib"},
  {"question":"What is a hyperparameter?","options":["Model parameter learned during training","Parameter set before training","Feature in dataset","Loss value"],"answer":"Parameter set before training"},
  {"question":"What does cross-validation do?","options":["Tests on unseen data multiple times","Splits data once","Removes outliers","Encodes labels"],"answer":"Tests on unseen data multiple times"},
  {"question":"What is the bias-variance tradeoff?","options":["Balance between model complexity and generalisation","Speed vs accuracy","Training vs test size","None"],"answer":"Balance between model complexity and generalisation"},
  {"question":"Which algorithm builds decision trees iteratively?","options":["SVM","Gradient Boosting","KNN","Naive Bayes"],"answer":"Gradient Boosting"},
],
"System Design": [
  {"question":"What does CAP theorem state?","options":["Three guarantees: Consistency, Availability, Partition tolerance — only 2 at a time","Three features of SQL","Network speed limits","None"],"answer":"Three guarantees: Consistency, Availability, Partition tolerance — only 2 at a time"},
  {"question":"What is a load balancer?","options":["Distributes traffic across servers","Stores data","Manages database","Caches responses"],"answer":"Distributes traffic across servers"},
  {"question":"What is horizontal scaling?","options":["Adding more power to one server","Adding more servers","Upgrading RAM","None"],"answer":"Adding more servers"},
  {"question":"What is a CDN?","options":["Central Database Network","Content Delivery Network","Centralised DNS","None"],"answer":"Content Delivery Network"},
  {"question":"What is the purpose of caching?","options":["Permanent storage","Faster data retrieval","Security","Logging"],"answer":"Faster data retrieval"},
  {"question":"What is a microservices architecture?","options":["One large application","Small independent services","Database design","API gateway"],"answer":"Small independent services"},
  {"question":"What does REST stand for?","options":["Reliable State Transfer","Representational State Transfer","Remote Server Technology","None"],"answer":"Representational State Transfer"},
  {"question":"What is a message queue?","options":["Database table","Async communication buffer","API endpoint","Cache layer"],"answer":"Async communication buffer"},
  {"question":"Which database is best for unstructured data?","options":["MySQL","PostgreSQL","MongoDB","SQLite"],"answer":"MongoDB"},
  {"question":"What is database sharding?","options":["Backup strategy","Splitting data across multiple databases","Indexing","Replication"],"answer":"Splitting data across multiple databases"},
  {"question":"What is the purpose of an API gateway?","options":["Direct database access","Single entry point for microservices","Cache storage","Load balancing only"],"answer":"Single entry point for microservices"},
  {"question":"What is eventual consistency?","options":["Data is always consistent","Data becomes consistent over time","No consistency","Immediate sync"],"answer":"Data becomes consistent over time"},
  {"question":"What is a reverse proxy?","options":["Client-side cache","Server-side intermediary","Database replication","DNS server"],"answer":"Server-side intermediary"},
  {"question":"What does ACID stand for?","options":["Atomicity, Consistency, Isolation, Durability","Access, Control, Index, Data","None","Auto, Cache, Index, Delete"],"answer":"Atomicity, Consistency, Isolation, Durability"},
  {"question":"What is rate limiting?","options":["Slowing down database","Controlling API request frequency","Network bandwidth","Cache expiry"],"answer":"Controlling API request frequency"},
  {"question":"Which pattern avoids cascading failures?","options":["Singleton","Circuit Breaker","Observer","Factory"],"answer":"Circuit Breaker"},
  {"question":"What is consistent hashing?","options":["Hash function for passwords","Distributing data across nodes with minimal redistribution","SQL hashing","None"],"answer":"Distributing data across nodes with minimal redistribution"},
  {"question":"What is database replication?","options":["Copying data to multiple servers","Deleting duplicate rows","Schema migration","None"],"answer":"Copying data to multiple servers"},
  {"question":"What is a write-through cache?","options":["Writes to cache only","Writes to cache and DB simultaneously","Writes to DB, reads from cache","None"],"answer":"Writes to cache and DB simultaneously"},
  {"question":"What is WebSocket used for?","options":["One-way HTTP","Full-duplex real-time communication","File transfer","Email protocol"],"answer":"Full-duplex real-time communication"},
],
}

# ── Fetch from Open Trivia DB (Category 18 = Computers) ─────────────────────

def fetch_opentdb(amount=10):
    try:
        url = f"https://opentdb.com/api.php?amount={amount}&category=18&type=multiple&difficulty=medium"
        r = requests.get(url, timeout=10)
        data = r.json()
        if data.get('response_code') != 0:
            return []
        questions = []
        for item in data['results']:
            q = html.unescape(item['question'])
            correct = html.unescape(item['correct_answer'])
            options = [html.unescape(o) for o in item['incorrect_answers']] + [correct]
            random.shuffle(options)
            questions.append({"skill":"Computer Science","question":q,"options":options,"answer":correct})
        return questions
    except Exception as e:
        print(f"  opentdb fetch failed: {e}")
        return []

# ── Seed ─────────────────────────────────────────────────────────────────────

def seed():
    print("Connecting to MongoDB...")
    total_inserted = 0
    for skill, qs in QUESTIONS.items():
        col.delete_many({"skill": skill})
        docs = [{"skill": skill, **q} for q in qs]
        result = col.insert_many(docs)
        print(f"  [OK] {skill}: {len(result.inserted_ids)} questions inserted")
        total_inserted += len(result.inserted_ids)
    print("\nFetching from Open Trivia Database...")
    time.sleep(1)
    opentdb_qs = fetch_opentdb(10)
    if opentdb_qs:
        col.delete_many({"skill": "Computer Science"})
        result = col.insert_many(opentdb_qs)
        print(f"  [OK] Computer Science (opentdb): {len(result.inserted_ids)} questions inserted")
        total_inserted += len(result.inserted_ids)
    print(f"\nDone! Total questions in DB: {col.count_documents({})}")
    print(f"Skills available: {col.distinct('skill')}")

if __name__ == "__main__":
    seed()

    
    total_inserted = 0
    
    # Seed hardcoded questions
    for skill, qs in QUESTIONS.items():
        # Remove existing for this skill
        col.delete_many({"skill": skill})
        docs = [{"skill": skill, **q} for q in qs]
        result = col.insert_many(docs)
        print(f"  ✅ {skill}: {len(result.inserted_ids)} questions inserted")
        total_inserted += len(result.inserted_ids)
    
    # Fetch from opentdb
    print("\nFetching from Open Trivia Database...")
    time.sleep(1)  # Rate limit respect
    opentdb_qs = fetch_opentdb(10)
    if opentdb_qs:
        col.delete_many({"skill": "Computer Science"})
        result = col.insert_many(opentdb_qs)
        print(f"  ✅ Computer Science (opentdb): {len(result.inserted_ids)} questions inserted")
        total_inserted += len(result.inserted_ids)
    
    print(f"\n🎉 Done! Total questions in DB: {col.count_documents({})}")
    print(f"   Skills available: {col.distinct('skill')}")

if __name__ == "__main__":
    seed()
