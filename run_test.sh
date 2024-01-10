export LRS_HOME='./_test_home'

# create, and assure that the directory is empty, otherwise exit
mkdir -p $LRS_HOME
if [ "$(ls -A $LRS_HOME)" ]; then
    echo "Directory $LRS_HOME is not empty. Please empty it and try again."
    exit 1
fi

# start the server and iserver
nohup sh -c "lires server" > $LRS_HOME/nohup.out &
nohup sh -c "lires iserver" > $LRS_HOME/nohup.out &

# wait for the server to start
echo "Waiting for the server to start..."
sleep 3

# run test cases
echo "Running test cases..."
python3 -m unittest discover -s test -p 'test_*.py'


echo "Cleaning up..."

# kill all the processes
kill $(ps aux | grep '[l]ires' | awk '{print $2}')
# remove the directory
rm -rf $LRS_HOME