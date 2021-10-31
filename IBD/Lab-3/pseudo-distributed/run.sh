# ssh service is not running; we have just installed it with apt-get when created hadoop-base
/etc/init.d/ssh start

start-dfs.sh
start-yarn.sh

# we need to keep container busy to keep it alive
while true; do sleep 1000; done