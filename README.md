### Algo dimension 

Author : Remy ADDA & David ZERAH

##### Stack 

- Python 3.6
- Docker 


#### Building

```shell   

sudo docker build -t <CONTAINER_NAME>.

```


#### RUNNING 

Checking the opening port before

```shell


sudo docker run -v PATH:/src -p 5000:80 -d -t --restart always <CONTAINER_NAME>

```

##### HELP RUNNING PARAMETER

- -v : to specify the path
- -d : to run on a background task
- -t : to check logs real time
- -p 5000:80 : the port 80 is open and flask is running on the port 5000, so we specify which port