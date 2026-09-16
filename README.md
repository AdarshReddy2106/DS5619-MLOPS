# Lab 6 — Containerize and Serve a Detector

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python generate_for_student.py --student-id 102301018
```

This overwrites data/fixtures/ with your own synthetic CCTV images — same file names, same two
camera profiles, always at least one detectable "vehicle" per image, generated deterministically from
your student ID.

## Task Implementation

### Image Upload Handling

Implemented `load_image_from_upload()` to load an uploaded image file and convert it into a PIL Image.
* Reads the uploaded file as raw bytes using `file_storage.read()`.
* Wraps the file contents in an in-memory stream using `io.BytesIO()`.
* Opens the image using `Image.open()`.
* Converts the image to RGB using `.convert("RGB")`.

This ensures that uploaded images are consistently converted to the RGB format expected by the detector.

### Detector Inference

Implemented `run_detection()` to perform vehicle detection on the uploaded image.
* Calls `det.detect(image)` to obtain the detection results.
* Calculates the total number of detections.
* Converts the detections into COCO-style annotation dictionaries using `det.detections_to_coco()`.

The resulting response contains the total detection count along with the corresponding list of detections.

### `/detect` route

Implemented the `/detect` POST route to connect the uploaded image with the detector.
* Checks whether an image file is provided under the `"image"` key.
* Returns a `400` response if the image file is missing.
* Loads the uploaded image using `load_image_from_upload()`.
* Passes the image to the detector using `run_detection()`.
* Returns the detection results as a JSON response.


### Docker Implementation

* Copies and installs the required dependencies from `requirements.txt`.
* Copies the `src/` directory into the Docker image.
* Exposes port `8080` for the Flask application.
* Starts the Flask application using `python3 src/app.py`.

## Verification

The Flask application was first tested locally using:

```bash
python src/app.py 
```

The Docker image was then built successfully using:

docker build -t week6-detector .

ran using:

docker run --rm -p 8080:8080 week6-detector

The running container was verified using the following API requests:

Health Check

curl http://localhost:8080/health

Detection Test

curl -F "image=@data/fixtures/camera_A_daylight/000.jpg" http://localhost:8080/detect

Both the /health and /detect endpoints were successfully verified against the running Docker container.
