# The config image contains instructions for Antithesis for how to set up your
# system. At minimum it consists of a `docker-compose.yaml`. Additional files
# used dufing setup may be added later.

# Start from an empty image:
FROM scratch

# Copy docker-compose.yaml and environment file:
COPY ./docker-compose.yaml docker-compose.yaml
COPY ./.env .env
