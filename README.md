# Environment

Install packages: `pip install -r requirements.txt`.
Download additional files: `make download`. 
Preprocess additional files: `make preprocess`.

If you changed list of packages:

1. Add new package to `./requirements.txt` and `./docker/Dockerfile`
2. Build docker image `docker build -t tsdaemon/classic-python .`
3. Push docker image `docker push tsdaemon/classic-python`

# Start

Start local server: `make server`.

Web-client will be available at `http://localhost:8000`.

# Testing

Smoke test: `make testworks`.
Speed test: `make testspeed` 


