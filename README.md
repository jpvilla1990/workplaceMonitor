# workplaceMonitor

Back End to classify persons in workplace by being working or not using YOLOv6 capturing videos from Ip cameras.
The Backend classify persons and two actions, working and nonworking. Using YOLO the persons are classified, and then by comparing several frames and the position of the squarebox, the backend will classify a person as nonworking if remains in the same position for long time.

In the folder data/imagesDatabase all the original images and its classification will be stored, the back end uses a mysql database
In the folder data/videoPersonsIdle all the videos with the persons nonworking will be stored
The database contains 3 tables:
- frames: each captured frame with its timestamp and a flag to indicate if already the persons have been detected and the action has been detected.
- objects: each person detected in each frame with its coordinates and foreign key with table frames, in here the persons are classified per frame but not compared with different frames
- persons: the persons from the table objects has been compared accross several frames to figure out if the person has been in the same position for long or not depending on the configuration and will be tagged as idle in such case

## Set Up:

First the docker image has to be build with the script dockerbuild.sh
Then use the docker-compose file in the folder deployment changing configurations in the file config.yml in the same folder deployment:
to start: docker-compose up -d
to stop: docker-compose stop

There are two persistent volume where the data will be generated, rely on those to see the images and logs

### Configuration:
Most relevant configurations from config.yml:
yolo.desiredConfidence: level of confidence to classify a person, YOLO will generate several boxes and classify them as persons with a certain level of confidence, this parametes will discard persons will confidence lower than this thresgold (default 50%)
yolo.framesPerSecond: frames per second capture from the IP cameras (default 1 per second), higher value means more resources consumed, recommende keep it maximum as the default value
actions.boxTolerance: tolerance which the back end will determined two boxes from different frames correspond to the same object in the same position, this will affect the working/nonworking classification (default 2%)
actions.idleFrames: how many consecutive frames is tolerated for a person to be in the same position before being classified as nonworking (default 5 frames)
actions.maxTimestampDifference: max difference between different frames to consider same person (default 1 second)
prediction.sleepPrediction: delay from prediction to prediction (default 1 second), must be more or equal than the value yolo.framesPerSecond, otherwise the classification subprocess will go faster than the capture subprocess
cameras.cameraN: dictionary with the cameras to be captured, the system support multiple cameras, only create more cameras with the index camera and the number, and assign the entry point to the camera, the camera is captured via TCP protocol, UDP is not supported.

### Debugging:
Relay in the file data/logs/log.txt, this will give hints about errors during the back end execution

## Usage

After the backend is running the container will be assigned to the port 8080 (can be modified from the docker-compose.yml file), use the following paths to interact with the backend:

- localhost:8080/cameraCapture/start : start capture from cameras IP
- localhost:8080/cameraCapture/stop : stop capture
- localhost:8080/predictor/start : start predictions from captured frames (YOLOv6 running as a process in docker sometimes creates deadlocks, if the predictor stops generating images trigger this command frequently, around every 5 minutes)
- localhost:8080/predictor/stop : stop predictions
- localhost:8080/reset : reset database and captured images, recommended to run this every day to avoid excess storage.

The backend will fill the database with all the needed information to enable the creation of any kind of efficiency reports, as well the videos of persons non working will be stored in the folder mentioned beforehand.

## Notes

- The predictor relies on the pretrain model from YOLOv6, therefore may behave differently between one to other environment and surroundings, therefore is better to play with the config file (tolerance) to find the best trade off
- The algorithm does not detect 100% all persons so this backend should not be a primary source or efficiency report, rather it should be an assitant tool where each generated video is reviewed to describe tendencies in the workplace
- The back end was tested in a development environment, hence for in production set up is suggested to test and if necesary extend the code without forgetting mentioning the author

## Tech Stack:
python3, pytorch, uvicorn, fastApi, mysql, YOLOv6, docker

JuanPabloVillaSerna@jpvilla1990@gmail.com
