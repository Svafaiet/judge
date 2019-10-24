#!/bin/bash

# run a docker with $1 name made from image $2
docker run -name $1 -p 8000:8000 --rm -it $2
