# Docker verification

Fill this in after you build and run your container (see README.md,
"Part 2 — Dockerfile"). This is how we confirm your container actually works, since an
automated grader running in a sandbox may not always have Docker-in-Docker
available.

## Build

Paste the command you ran and its final output line (the one showing the
built image ID/tag):

docker build -t week6-detector .

writing image sha256:414c255e1c7057c809d4e19daaef4b9900fea751e54dd0af30f0d98f901e4d8c                                                                      0.0s
 => => naming to docker.io/library/week6-detector 

## Run

Paste the command you used to start the container (should map a host port
to the container's 8080):

docker run --rm -p 8080:8080 week6-detector

## Verify

Paste the exact `curl` commands and their JSON output for both endpoints,
run against the running container (not against `python src/app.py` directly
— the point is to prove the *container* works):

curl http://localhost:8080/health
response : {"status":"ok"}

curl -F "image=@data/fixtures/camera_A_daylight/000.jpg" http://localhost:8080/detect
response : {"count":5,
            "detections":[  {"bbox":[31,8,38,19],"category_id":8,"id":0,"image_id":0,"score":0.98},
                            {"bbox":[17,28,34,16],"category_id":12,"id":1,"image_id":0,"score":0.938},
                            {"bbox":[52,30,6,17],"category_id":4,"id":2,"image_id":0,"score":0.856},
                            {"bbox":[285,102,24,20],"category_id":4,"id":3,"image_id":0,"score":0.98},
                            {"bbox":[135,124,19,23],"category_id":3,"id":4,"image_id":0,"score":0.98}
            ]}