# IR 2017
A simple information retrieval system using **python3** and spark.

## How to run the project

plz make sure you have installed related component such as `MySQL`, `Redis`, `Spark` and corresponding executed environment. 

Firstly, you should run `update/__init__.py`, which would call crawler and then build indexes and model such as `word's posting list` and `word co-occurrence model`.  

Secondly, plz run `main.py`, which would start a server and supply many service such as  `balabala`. 

Last but not least, run `ir201712-front_end/search_engine.py` to start the front-end server. OK, visit `127.0.0.1:5000` by browser to enjoy it.

## How to install

### git

1. install git
2. set initial params of git
  1. `git config --global user.name <github_name>`
  2. `git config --global user.email <github_email>`
3. `git clone https://github.com/xuesu/ir201712.git`

### mysql
4. install mysql
  - In Ubuntu: `sudo apt install mysql-server`
5. open mysql terminal: (Attention, we should always use this charset **'UTF8mb4'**)
    - Create a new db to avoid database-scale change in program: `CREATE DATABASE ir character set UTF8mb4 collate utf8mb4_bin;`
    - Then create a test db: `CREATE DATABASE ir_test character set UTF8mb4 collate utf8mb4_bin;`
    - Create a new user: `CREATE USER 'IRDBA'@'localhost' IDENTIFIED BY 'complexpwd';`
    - Grant privilege to the user: `GRANT ALL ON ir.* TO 'IRDBA'@'localhost';GRANT ALL ON ir_test.* TO 'IRDBA'@'localhost';`

### Redis
6. install Redis
    - In Ubuntu: `sudo apt-get install redis-server`

### virtualenv

1. install anaconda
2. build a new virtualenv `conda create -n <env_name> python=3`
3. activate the virtualenv `source activate <env_name>`
4. `pip install -r requirements.list`

### spark

1. download & unzip https://www.apache.org/dyn/closer.lua/spark/spark-2.2.1/spark-2.2.1-bin-hadoop2.7.tgz
2. edit the path:
    1. in ubuntu: 
    ```
    export SPARK_HOME="/XXXX/spark-2.2.1-bin-hadoop2.7"
    export PYTHONPATH=$SPARK_HOME/python/:$PYTHONPATH
    export PYTHONPATH=$SPARK_HOME/python/lib/py4j-0.9-src.zip:$PYTHONPATH
    ```
3. If you are using pyspark terminal, you can start now.
4. If you are using pycharm, you need add `<spark_home>/python/pyspark` & `<spark_home>/python/lib/py4j-0.9-src.zip` into content root.

## emotions
It takes about 810MB memory, 囧

1. `cd emotions`
2. build a new virtualenv `conda create -n <env_name2> python=2`
    - NOTE: This project is written in a **different** language!
3. activate the virtualenv `source activate <env_name2>`
4. `pip install -r requirements.list`
5. `python demo_service.py`


## How to develop
1. Obey the basic coding rule if you can. BUT it is ok to write in your own style.
2. Try to write some test cases.
3. Always pull master and push dev!
  1. `git pull master`
  2. `git add *`
  3. `git commit -m "<my_change>"`
  4. `git push <branch>:dev`


## How to read the code?

Plz try to read `update/__init__.py` for begining.