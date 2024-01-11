export LRS_HOME='./test/_test_home'
echo "LRS_HOME: $LRS_HOME"
echo "PWD: $PWD"

# create, and assure that the directory is empty, otherwise exit
mkdir -p $LRS_HOME
if [ "$(ls -A $LRS_HOME)" ]; then
    echo "Directory $LRS_HOME is not empty. Please empty it and try again."
    exit 1
fi

# run test cases
python3 test/main.py

# clean up
echo "Test cases finished. Will clean up..."
read -p "Press enter to continue..."
rm -rf $LRS_HOME