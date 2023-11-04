#!/bin/sh

# function to check if a service is ready
check_service() {
  url=$1
  until $(curl --output /dev/null --silent --head --fail $url); do
    printf '.'
    sleep 5
  done
}

# check if Weaviate is ready
check_service $WEAVIATE_DB_HOST/v1/.well-known/ready

# check if MongoDB is ready
check_service $MONGO_DB_HOST

# start your application
exec "$@"
