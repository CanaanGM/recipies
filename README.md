

TODO:
---
- [ ] diagrams  
- [ ] Better Readme
- [ ] Technical docs
- [ ] front-end ?


 ## features: 
 + development/deployment thru: docker-compose
 + TDD using django's built in Test suite
 + Automation thru: github actions 
+ user authentication via Token authentication
+ django admin for managing the database models
+ OpenApi(swagger)


##  run locally:
1. clone the repo
2. ```docker-compose up ```
3. go to : ```localhost:8000/docs``` 

## run tests:
```docker-compose run --rm app sh -c "python manage.py test" ```

## Local development:
#### commands :
 + start an app: 
	- ``` docker-compose run --rm app  sh -c "python manage.py startapp appname" ```
+ make migrations: 
	- ``` docker-compose run --rm app sh -c "python manage.py makemigrations ```
	- the app will auto apply the migrations at startup.
+ Test:
	- ``` docker-compose run app sh -c "python manage.py test"```
+ build the docker image with either : 
	+  ```docker-compose build ```
	+ ``` docker build .```


