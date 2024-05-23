
DOCKER_IMAGE_NAME = "lires"

test-build:
	docker build -f docker/test.Dockerfile -t $(DOCKER_IMAGE_NAME):test .
test-run:
	docker run --rm -it \
		-v ./:/Lires \
		-v /Lires/lires/vector/lib \
		-v ./test/_cache:/_cache \
		-e LRS_HOME=/Lires/test/_sandbox \
		$(DOCKER_IMAGE_NAME):test /usr/local/bin/python3 ./test/main.py
test-inspect:
	docker run --rm -it \
		-v ./:/Lires \
		-v /Lires/lires/vector/lib \
		-v ./test/_cache:/_cache \
		-e LRS_HOME=/Lires/test/_sandbox \
		$(DOCKER_IMAGE_NAME):test tmux
test-clean:
	docker rmi $(DOCKER_IMAGE_NAME):test


obsidian-build:
	cd plugins/obsidian && npm install && npm run build
doc-build:
	cd docs && npm install && npm run build
web-build:
	cd lires_web && npm install && npm run build
build: obsidian-build doc-build web-build

docker-build:
	docker build -f docker/Dockerfile -t $(DOCKER_IMAGE_NAME):latest .