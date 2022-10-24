all: clean build

build:
	cd frontend; npm run build
	mkdir release
	mv frontend/build release/web
	cp backend/*.py backend/requirements.txt backend/start.sh release
	tar caf release.tar.gz release

clean:
	rm -r release