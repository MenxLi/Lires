
DOCKER_IMAGE_NAME = "lires"

test-build:
	docker build -f docker/test.Dockerfile -t $(DOCKER_IMAGE_NAME):test .
test-run:
	docker run --rm -it \
		-v ./:/Lires \
		-v ./test/_cache:/_cache \
		$(DOCKER_IMAGE_NAME):test /bin/bash ./run_test.sh
test-inspect:
	docker run --rm -it -v ./:/Lires $(DOCKER_IMAGE_NAME):test /bin/bash
test-clean:
	docker rmi $(DOCKER_IMAGE_NAME):test