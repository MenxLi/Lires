export LRS_HOME='./_test_home'

# create, and assure that the directory is empty, otherwise exit
mkdir -p $LRS_HOME
if [ "$(ls -A $LRS_HOME)" ]; then
    echo "Directory $LRS_HOME is not empty. Please empty it and try again."
    exit 1
fi

# run test cases
echo "Running test cases..."
python3 -m unittest discover -s test -p 'test_*.py'

# remove the directory
rm -rf $LRS_HOME