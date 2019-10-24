cp templates/server_settings.py $1/
docker build $1 -f Dockerfile -m 50m --memory-swap 40m 
rm -rf $1/server_settings.py
