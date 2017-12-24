# IR 2017
A simple information retrieval system using **python3** and spark.

## How to install
1. install git
1. set initial params of git
	1. `git config --global user.name <github_name>`
	1. `git config --global user.email <github_email>`
2. `git clone https://github.com/xuesu/ir201712.git`
4. install mysql
	- In Ubuntu: `sudo apt install mysql-server`
5. open mysql terminal:
    - Create a new db to avoid database-scale change in program: `CREATE DATABASE ir;`
    - Then create a test db: `CREATE DATABASE ir_test;`
    - Create a new user: `CREATE USER 'IRDBA'@'localhost' IDENTIFIED BY 'complexpwd';`
    - Grant privilege to the user: `GRANT ALL ON ir.* TO 'IRDBA'@'localhost';GRANT ALL ON ir_test.* TO 'IRDBA'@'localhost';`
1. install anaconda
2. build a new virtualenv `conda create -n <env_name>`
3. activate the virtualenv `source activate <env_name>`
3. `pip install -r requirements.list`



## How to develop
1. Obey the basic coding rule if you can. BUT it is ok to write in your own style.
2. Try to write some test cases.
2. Always pull master and push dev!
	1. `git pull master`
	1. `git add *`
	2. `git commit -m "<my_change>"`
	3. `git push <branch>:dev`

