
# Docker Deployment
Running Lires with docker provide another level of isolation and security.  

## Basic usage

### Start
```sh
# build the image
docker build -f docker/Dockerfile -t lires:runtime .

# run the container, map the port 8080 to the host machine
docker run -d -p 80:8080 -v </path/to/data>:/root/.Lires --name lrs lires:runtime
```

### Management
```sh
# user management
docker exec -it lrs lrs-user ...

# check the logs
docker exec -it lrs lrs-log ...

# or check output by docker logs
docker logs -f lrs
```

## Change the configuration
The docker image essentially runs the [`lrs-cluster`](./gettingStarted.md#cluster-startup) command with the configuration file `/root/.Lires/container-cluster.yaml`. 
Which should be mounted to the host machine for easy access and modification.

::: info  
Although you may change the [environment variables](./enviromentVariables.md) with `docker run -e ...`, 
it is recommended to modify them in the cluster configuration file, 
to make sure it will not be overwritten by the values set with the configuration file.
:::  

## Limit the resources
An advantage of running the app with docker is that you can limit the resources of the container.

To limit the memory and cpu usage, you can use the `--memory` and `--cpus` flags.
```sh
docker run --memory 4g --cpus 2 ...
```

To limit the disk usage, you can use the docker volume driver, 
for example, first create a volume with limited size, 
then mount it to the container.
```sh
# create a volume with 10G size
docker volume create --driver local --opt type=btrfs --opt o=size=10G lrs-data

# run the container with the volume
docker run -v lrs-data:/root/.Lires ...
```
for more information, see [docker - driver specific options](https://docs.docker.com/reference/cli/docker/volume/create/#driver-specific-options).

