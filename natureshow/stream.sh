for((;;)); do \
sleep 1; \
done

for((;;)); do \
    raspivid -o - -t 0 -vf -hf -fps 25 -b 500000 -w 1280 -h 720 | ffmpeg -re -ar 44100 -ac 2 -acodec pcm_s16le -f s16le -ac 2 -i /dev/zero -f h264 -i - -vcodec copy -acodec aac -ab 128k -g 50 -strict experimental -f flv rtmp://$STREAM_URL/$STREAM_APP/$STREAM_KEY
    sleep 1; \
done
