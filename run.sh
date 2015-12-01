 #!/bin/bash
for i in `seq 1965 2015`;
do
  start=$i
  python scraper.py $start
done
