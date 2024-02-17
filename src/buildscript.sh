cd amm
docker build -t amm . --network=host
cd ../node
docker build -t node . --network=host
cd ../node_attacker
docker build -t node_attacker . --network=host
cd ../monitor
docker build -t monitor . --network=host
cd ../oracle
docker build -t oracle . --network=host
cd ../miner
docker build -t miner . --network=host