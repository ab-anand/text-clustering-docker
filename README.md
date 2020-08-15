## Text Clustering API
Implementation of a text clustering algorithm using Kmeans clustering in order to derive quick insights from unstructured text.
Can be used as a boilerplate code for text clustering applications with Flask and Docker support.

### Environment
* Python 3.x
* Flask
* Docker
* Swagger

### Docker Setup

* Install Docker
* Run git clone 

```$ git clone https://github.com/ab-anand/text-clustering-docker.git```

* Navigate to the folder 

```$ cd /path/to/text-clustering-docker```
* Build the container
 
 ```$ docker build -t clustering-api .```
* Run the container.

```$ docker run -d -p 8000:8000 clustering-api```


### Swagger

* Hit `http://localhost:8000/apidocs` to play with the api.
* The endpoint returns a **zipped** file with an `xls` file of outputs inside.