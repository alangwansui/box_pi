while true
do
  ps -ef | grep sql.py | grep -v grep
  if [ $? -eq 0 ]; then
    sleep 10
  else
    python /home/pi/sql.pyc &
  fi
done
