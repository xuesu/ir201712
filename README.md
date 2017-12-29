# IR 2017
A simple information retrieval system using **python3** and spark.

## How to install
### git
1. install git
1. set initial params of git
	1. `git config --global user.name <github_name>`
	1. `git config --global user.email <github_email>`
2. `git clone https://github.com/xuesu/ir201712.git`

### mysql
4. install mysql
	- In Ubuntu: `sudo apt install mysql-server`
5. open mysql terminal: (Attention, we should always use this charset **'UTF8mb4'**)
    - Create a new db to avoid database-scale change in program: `CREATE DATABASE ir character set UTF8mb4 collate utf8mb4_bin;`
    - Then create a test db: `CREATE DATABASE ir_test character set UTF8mb4 collate utf8mb4_bin;`
    - Create a new user: `CREATE USER 'IRDBA'@'localhost' IDENTIFIED BY 'complexpwd';`
    - Grant privilege to the user: `GRANT ALL ON ir.* TO 'IRDBA'@'localhost';GRANT ALL ON ir_test.* TO 'IRDBA'@'localhost';`
    
### virtualenv
    
1. install anaconda
2. build a new virtualenv `conda create -n <env_name>`
3. activate the virtualenv `source activate <env_name>`
3. `pip install -r requirements.list`

### spark

1. download & unzip https://www.apache.org/dyn/closer.lua/spark/spark-2.2.1/spark-2.2.1-bin-hadoop2.7.tgz
1. edit the path:
    1. in ubuntu: 
    ```
    export SPARK_HOME="/XXXX/spark-2.2.1-bin-hadoop2.7"
    export PYTHONPATH=$SPARK_HOME/python/:$PYTHONPATH
    export PYTHONPATH=$SPARK_HOME/python/lib/py4j-0.9-src.zip:$PYTHONPATH
    ```
3. If you are using pyspark terminal, you can start now.
4. If you are using pycharm, you need add `<spark_home>/python/pyspark` & `<spark_home>/python/lib/py4j-0.9-src.zip` into content root.



## How to develop
1. Obey the basic coding rule if you can. BUT it is ok to write in your own style.
2. Try to write some test cases.
2. Always pull master and push dev!
	1. `git pull master`
	1. `git add *`
	2. `git commit -m "<my_change>"`
	3. `git push <branch>:dev`

