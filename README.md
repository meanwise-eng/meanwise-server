#Meanwise Backend
This is the brand new backend written for Meanwise in Python using Django.

##Installation
Installation comprises of standard steps used for deploying any Django application.

### Installing Python Packages
```
$ git clone git@github.com:meanwise-eng/meanwise-server.git
$ cd meanwise-server
$ sudo easy_install pip
$ pip install virtualenv
$ pip install virtualenvwrapper
$ source virtualenvwrapper.sh
$ mkvirtualenv --python=/usr/local/bin/python3 meanwise
```
Note: Please check once where python3 is installed in your system if above command shows an error please replace the location with where python3 is installed in your system.

If you're a linux user you might need to do:   ``` sudo apt-get install python3-dev ```
```
$ workon meanwise
(meanwise)$ pip install -r requirements.txt
```

### Installing Postgresql
For people on Mac use `brew install postgresql` to install latest version of Postgresql.
Make sure that you are running v >= 9.4 of Postgresql.  
After completing installation run the following commands. We are going to create a new user and database for Meanwise.
```
$ createdb -Uroot meanwise
$ psql -Uroot -d meanwise

meanwise=# CREATE ROLE meanwise WITH LOGIN;
meanwise=# ALTER ROLE meanwise WITH PASSWORD 'password';
meanwise=# GRANT ALL ON DATABASE meanwise TO meanwise;
```

### Creating Schema
Once we have Django app and Postgresql installed it's now time to create the 
schema. Go to `meanwise_backend` and run the following commands..
```
(meanwise)$ ./manage.py migrate
(meanwise)$ ./manage.py createsuperuser
```
Follow the instructions to create a super user.

### Running the server
Meanwise Backend already includes a uWSGI server and config for running it. 
Before running the following commands make sure you edit `uwsgi.dev.ini` located in `meanwise_backend/meanwise_backend`.  
Here's a sample config:
```
[uwsgi]
# Environment Variables
env = ENVIRONMENT=development
env = DATABASE=default

chdir=<PATH_TO_MEANWISE_BACKEND>
module=meanwise_backend.wsgi:application
master=True
pidfile=<PATH_TO_MEANWISE_BACKEND>/meanwise_backend.pid
vacuum=True
max-requests=5000
daemonize=<PATH_TO_MEANWISE_BACKEND>/log/uwsgi.log
home=<PATH_TO_MEANWISE_BACKEND>/env/
http=127.0.0.1:49100    # Use this to run it on port 49100
socket=<PATH_TO_MEANWISE_BACKEND>/meanwise_backend.sock  # Use this to run it on socket
py-autoreload=5
```
Now run the following commands

```
(meanwise)$ mkdir logs
(meanwise)$ uwsgi --ini meanwise_backend/uwsgi.dev.ini
```
You can check <PATH_TO_MEANWISE_BACKEND>/log/uwsgi.log for logs. To stop and start the server again you can either reload or stop and start the server again.
```
(meanwise)$ uwsgi --reload meanwise_backend.pid
(meanwise)$ uwsgi --stop meanwise_backend.pid
(meanwise)$ uwsgi --ini meanwise_backend/uwsgi.dev.ini
```

### Deploying using fabric
Current there is a very basic deployment script added to the repo. The deployment script can be used to deploy code on staging. Use the following command for that.
```
fab -f meanwise_backend/fabfile.py -R staging deploy
```

### [Documentation for API endpoints](https://github.com/meanwise-eng/meanwise-server/tree/master/docs)
