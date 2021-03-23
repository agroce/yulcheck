docker exec $1 bash -c "cd ~/solidity/test/yulcheck; git pull; cp checkyul.py .."
docker exec $1 bash -c "cd ~/solidity/test; python checkyul.py \"fuzz_solc/queue/id*\""
