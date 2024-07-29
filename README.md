# update-notifier
a telegram bot that will send updates to a channel whenever an update has been released for an app store app. apps are checked for updates every 20 minutes. now uses a database for portability!

## running locally
install python, clone the repo, then move `.env.example` to `.env` and populate it with your variables. then see usage with:

`(source .env && python src/update_notifier.py)`

make sure `DATABASE` is a file that doesnt exist (on first run). the database will be created for you.

## running using docker
install docker/podman and docker-compose/podman-compose respectively, clone the repo, then modify the `docker-compose.yml`.

docker/podman will throw an error if `DATABASE` doesn't exist, so make sure to `touch data.db` before starting the container.

you should use the native python script or use docker to add new apps to monitor to the database.

these docs suck by the way, it should be easy enough to figure everything out though !!
