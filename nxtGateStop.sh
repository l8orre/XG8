kill -9 `ps x | grep nxtGate.py | grep -v grep | awk '{print $1}'`

