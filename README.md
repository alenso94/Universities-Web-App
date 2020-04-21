# Universities Web App

Students all over the world are looking for universities to pursue higher education. The purpose of University WebApp is to help people to get a list of universities in different countries, 
their domain names, web pages etc.. It is a prototype of Cloud application deployed on AWS EC2 instance. This app makes calls to an external API hosted in http://universities.hipolabs.com/search 
in order get more information about different universities based on country and the university name. The project supports an application that is developed in flask and python and deployed 
on a docker. The data extracted from the application API is stored in a cassandra database. The response from the source is in the form of JSON but displayed in human readble HTML format. 
The information of interest are Name, Country, State-Province, Domains, AlphaTwoCode and Webpages.

Using this app, the user is able to view a list of universities, insert new universities into the list, update the university details and delete the universities. 

This will work on the following aspects of Cloud applications:

 * REST-based service interface.
 * Interaction with external REST services.
 * Use of on an external Cloud database for persisting information.
 * Support for cloud scalability, deployment in a container environment.
 * Cloud security awareness.

## PROJECT SPECIFICATION
1. The application provides a dynamically generated REST API. The API must have a sufficient set of services for the selected application domain. The REST API responses must conform to REST standards (e.g. response codes).
2. The application makes use of an external REST service to complement its functionality.
3. The application uses a cloud database for accessing persistent information.
4. Implemented cloud security measures by Serving the application over https using Self-signed certificate. 
5. Implementation of load balancing of the application by Kubernetes based Load Balancing. 

## Interacting with Web Application 
### External API

#### *GET* @app.route('/universities/all')
Get the details of all the universities.

#### *GET* @app.route('/universities/all/view/<country>/<name>')
Get the list of all universities in the given country and with a given name

### REST-based Service Interface

#### *GET* @app.route('/')
The Home page of Universities WebApp

#### *GET* @app.route('/universities')
Get the list of all universities from the database.

#### *GET* @app.route('/universities/name/<name>')
Get the list of all universities with a given name. 

#### *GET* @app.route('/universities/country/<country>')
Get the list of all universities in a given country

#### *POST* @app.route('/universities')
Add a new university to the database. The user must provided the following:

 * name
 * id
 * country
 * web_pages
 * domains
 * alpha_two_code

#### *PUT* @app.route('/universities')
Update the webpage of an existing university in the database. The user must provide the following:

 * name
 * web_pages

#### *DELETE* @app.route('/universities')
Deletes a university record from the database. The user must provide the following:

 * name

 ## Initial setup

1. Login to AWS Educate, start a t2.medium instance and log into it. 
2. Install docker to use it

```
sudo apt update
sudo apt install docker.io
```

3. Run a Cassandra instance within docker by exposing port 9042.

```
sudo docker run --name cassandra-test -p 9042:9042 -d cassandra:latest
```

4. Move universities_stats.csv data and copy it into the container.

``` 
sudo docker cp universities_stats.csv cassandra-test:/home/universities_stats.csv
```

5. Interact with our Cassandra via its native command line shell client called ‘cqlsh’ using CQL.

```
sudo docker exec -it cassandra-test cqlsh
```

6. Inside the Cassandra Terminal create a dedicated keyspace for the universities data to be inserted into.

```
CREATE KEYSPACE Universities WITH REPLICATION ={'class' : 'SimpleStrategy', 'replication_factor' : 1};
```

7. Create the table inside the keyspace, specifying all column names and types: 

```
CREATE TABLE Universities.stats (id int, domains text, country text, web_pages text, name text PRIMARY KEY, alpha_two_code text);
```

8. Copy the data from our csv into the database. We have to specify the insertion order as table columns have no intrinsic order within Cassandra: 

```
COPY universities.stats(id,domains,country,web_pages,name,alpha_two_code) FROM '/home/universities_stats.csv' WITH DELIMITER=',' AND HEADER=TRUE;
```

9. Create requirements.txt, Dockerfile and app.py

10. Default Port 80 is used to host the application. It is set in app.py as given below:

```
if __name__ == '__main__':
 	app.run(host='0.0.0.0', port=80)
```

11. Build the image

```
sudo docker build . --tag=cassandrarest:v1
```

12. Run it as a service, exposing the deploment to get an external IP

```
sudo docker run -p 80:80 cassandrarest:v1
```

 ## Cloud Security - HTTPS Implementation

13. Serve the application over https using Self-signed certificate.
 
A self-signed certificate is the one where the signature is generated using the private key that is associated with that same certificate. The client needs to "know and trust" the CA that 
signed a certificate, because that trust relationship is what allows the client to validate a server certificate. Web browsers and other HTTP clients come pre-configured with a list of 
known and trusted CAs, but obviously if you use a self-signed certificate the CA is not going to be known and validation will fail. If the web browser is unable to validate a server 
certificate, it will let you proceed and visit the site in question, but it will make sure you understand that you are doing it at your own risk.

Generate self-signed certificates easily from the command line using the command given below:

```
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
```

This command writes a new certificate in cert.pem with its corresponding private key in key.pem, with a validity period of 365 days. When you run this command, you will be asked a few 
questions.I answered this as given below:

```
Generating a 4096 bit RSA private key
......................++
.............++
writing new private key to 'key.pem'
-----
You are about to be asked to enter information that will be incorporated
into your certificate request.
What you are about to enter is what is called a Distinguished Name or a DN.
There are quite a few fields but you can leave some blank
For some fields there will be a default value,
If you enter '.', the field will be left blank.
-----
Country Name (2 letter code) [AU]:UK
State or Province Name (full name) [Some-State]:England
Locality Name (eg, city) []:Hackney
Organization Name (eg, company) [Internet Widgits Pty Ltd]:Cloud Computing Mini-Project
Organizational Unit Name (eg, section) []:
Common Name (e.g. server FQDN or YOUR name) []:localhost
Email Address []:
```

We can now use this new self-signed certificate in our Flask application by setting the ssl_context argument in app.run() to a tuple with the filenames of the certificate and private key 
files:

```
 if __name__ == '__main__':
    app.run(host='0.0.0.0', port=443, ssl_context=('cert.pem','key.pem'))
```

The port number has been set as 443 as we will be serving the application over https. 

14. Build the image and run it as a service, exposing the deployment to get an external IP. 

```
sudo docker build . --tag=cassandrarest:v1

sudo docker run -p 443:443 cassandrarest:v1
```

 ## Kubernetes Deployment

15. Inorder to implement kubernetes based LoadBalancer, install kubernetes using the command given below:
	
```
sudo snap install microk8s --channel=1.18 --classic
```

16. Having a private Docker registry can significantly improve your productivity by reducing the time spent in uploading and downloading Docker images. The registry shipped with MicroK8s is 
hosted within the Kubernetes cluster and is exposed as a NodePort service on port 32000 of the localhost. 

Install the registry using the command given below:

```
microk8s enable registry
```

17. To upload images we have to tag them with localhost:32000/your-image before pushing them. Add proper tagging using build as given below:

```
sudo docker build . -t localhost:32000/cassandra:registry
```

18. Push the image to the registry as it has been tagged correctly.

```
sudo docker push localhost:32000/cassandra
```

19. Pushing to this insecure registry may fail in some versions of Docker unless the daemon is explicitly configured to trust this registry. To address this we need to edit /etc/docker/daemon.json and add:

```
{
  "insecure-registries" : ["localhost:32000"]
}
```

20. The new configuration should be loaded with a Docker daemon restart:

```
sudo systemctl restart docker
```

21. Restart the container

```
sudo docker start cassandra-test
```

22. Create cdb.yaml file and deploy with our image as given below:

```
sudo microk8s kubectl apply -f cdb.yaml
```

23. To expose our cluster to the external world, create a service resource, which provides networking and IP support to our application’s pod as given below:

```
sudo microk8s kubectl expose deployment cassandra-deployment --type=LoadBalancer --port=443 --target-port=443
```

24. To see the pods and services created:

```
sudo microk8s kubectl get all
```

```
NAME                                       READY   STATUS    RESTARTS   AGE
pod/cassandra-deployment-b7cffc85f-bxftx   1/1     Running   37         18h
pod/cassandra-deployment-b7cffc85f-ldmnv   1/1     Running   37         18h

NAME                           TYPE           CLUSTER-IP      EXTERNAL-IP   PORT(S)         AGE
service/cassandra-deployment   LoadBalancer   10.152.183.39   <pending>     443:30888/TCP   18h
service/kubernetes             ClusterIP      10.152.183.1    <none>        443/TCP         18h

NAME                                   READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/cassandra-deployment   2/2     2            2           18h

NAME                                             DESIRED   CURRENT   READY   AGE
replicaset.apps/cassandra-deployment-b7cffc85f   2         2         2       18h
```

By default the kubernetes service allocates a port within range '30000-32767'.

25. Finally view the web app in the browser using the public DNS of AWS EC2 account along with this Nodeport that starts with '30xxx'. Don't forget to give https:// in front of the URL. 

26. After deploying on Kubernetes cluster and implementing LoadBalancer, GET requests are given on the browser as 
	
```
https://ec2-54-145-219-199.compute-1.amazonaws.com:30888
https://ec2-54-145-219-199.compute-1.amazonaws.com:30888/universities
https://ec2-54-145-219-199.compute-1.amazonaws.com:30888/universities/name/University of Leeds
https://ec2-54-145-219-199.compute-1.amazonaws.com:30888/universities/country/United Kingdom
https://ec2-54-145-219-199.compute-1.amazonaws.com:30888/universities/all
https://ec2-54-145-219-199.compute-1.amazonaws.com:30888/universities/all/view/United Kingdom/queen
```

NOTE: Public DNS will vary. 

POST requests are provided using curl commands on a terminal as given below:

```
curl -k -i -H "Content-Type: application/json" -X POST -d '{"id":1289,"domains":"uosl.uk", "country":"United Kingdom", "web_pages": "http://www.uosl.com", "name":"University of South London", "alpha_two_code":"GB"}' https://0.0.0.0:30888/universities
```

Response:

```
HTTP/1.0 201 CREATED
Content-Type: application/json
Content-Length: 73
Server: Werkzeug/1.0.1 Python/3.7.7
Date: Mon, 20 Apr 2020 19:43:29 GMT

{"message":"University added: /universities/University of South London"}
```

PUT requests are provided as given below:

```

curl -k -i -H "Content-Type: application/json" -X PUT -d '{"name":"University of South London","web_pages":"http://www.uniofsouthlo.ac.uk"}' https://0.0.0.0:30888/universities

```

Response:

```
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 75
Server: Werkzeug/1.0.1 Python/3.7.7
Date: Mon, 20 Apr 2020 19:44:15 GMT

{"message":"University updated: /universities/University of South London"}
```

DELETE requests are provided as given below:

```
curl -k -i -H "Content-Type: application/json" -X DELETE -d '{"name":"University of South London"}' https://0.0.0.0:30888/universities
```

Response:

```
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 75
Server: Werkzeug/1.0.1 Python/3.7.7
Date: Mon, 20 Apr 2020 19:45:16 GMT

{"message":"University deleted: /universities/University of South London"}
```

### Cleanup

27. Delete the Kubernetes deployment and LoadBalancer service using below commands:

```
sudo microk8s.kubectl delete deployment covidapp-deployment
sudo microk8s.kubectl delete service covidapp-deployment
```

28. Delete the Cassandra database instance by:

```
sudo docker rm cassandra-test
```

## Universities Web App built with:

* [Cassandra](http://cassandra.apache.org/doc/latest/) - Database used
* [Flask](http://flask.pocoo.org/docs/1.0/) - Web framework used
* [Universities List API](http://universities.hipolabs.com/search) - External API used
* [Kubernetes](https://microk8s.io/docs/registry-built-in) - Load balancing & Scaling
* [Encryption & Security](https://blog.miguelgrinberg.com/post/running-your-flask-application-over-https) - TLS protocol using 'adhoc' SSL

## Author

Alenso Joy Valiaveettil
	







