# upgrade script for the database from v1.6.2 to ...

cd $LRS_HOME/Database && \
mkdir files && \

# move everything from the old_database to the old_database/files except lrs.db and .trash
find . -maxdepth 1 -type f -not -name 'lrs.db' -exec mv {} ./files \; && \
find . -maxdepth 1 -type d -not -name '.trash' -not -name 'files' -not -name '.' -exec mv {} ./files \; && \
echo "Database files moved to the files directory" && \

# move index directory to the database directory
mv ../index . && \
echo "Index directory moved to the database directory" && \

echo "Database upgrade complete"