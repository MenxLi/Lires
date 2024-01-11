
DOCKER_IMAGE_NAME = "lires"

docker-test-build:
	docker build -f docker/test.Dockerfile -t $(DOCKER_IMAGE_NAME):test .

docker-test-run:
	docker run --rm -it -v ./:/Lires $(DOCKER_IMAGE_NAME):test /bin/bash ./run_test.sh

docker-test-inspect:
	docker run --rm -it -v ./:/Lires $(DOCKER_IMAGE_NAME):test /bin/bash

docker-test-clean:
	docker rmi $(DOCKER_IMAGE_NAME):test