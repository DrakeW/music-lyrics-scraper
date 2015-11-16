 #!/bin/bash
for i in `seq 1967 2015`;
do
  start=$i
  python scraper.py $start
done
