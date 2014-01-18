#/bin/bash
SUM="0"
while read VAL; do
   if [[ -z $VAL ]]; then
     continue
   fi
   VAL=$(sed 's/,/./;s/ //g' <<< $VAL)
   SUM="$SUM + $VAL"
   SUM=$(bc <<< $SUM)
done
echo $SUM
