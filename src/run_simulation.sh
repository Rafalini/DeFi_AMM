#!/bin/bash

docker kill $(docker ps -q) #kill living

sudo rm -rf ./output/*      #clean after all

cd amm
docker build -t amm . --network=host
cd ../miner
docker build -t miner . --network=host
cd ../monitor
docker build -t monitor . --network=host
cd ../oracle
docker build -t oracle . --network=host

cd ../node_attacker
docker build -t node_attacker . --network=host

cd ../node
docker build -t node . --network=host


docker-compose up --scale node=8 --scale miner=1 --remove-orphans #run them all