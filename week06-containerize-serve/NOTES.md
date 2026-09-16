# NOTES.md — Week 6: Containerize and Serve a Detector

**Student ID used with `generate_for_student.py`:**
<!-- paste the --student-id value you used -->
student_id: 102301018
seed: 1373709859

## Built image size

<!-- What image size did `docker images` report for week6-detector? -->

command: docker images 

REPOSITORY       TAG       IMAGE ID       CREATED              SIZE
week6-detector   latest    d3d717e2fb11   About a minute ago   189MB

## Swapping in a real checkpoint

<!-- What's the single biggest thing you'd change about this Dockerfile if
     src/mock_detector.py were swapped for a real torch-based checkpoint?
     (Think about what that does to build time and image size.) -->

If `src/mock_detector.py` were replaced with a real PyTorch-based detector, the biggest change I would make would be to **avoid bundling the large model checkpoint directly into the Docker image**.
PyTorch and its dependencies would already increase the image size and build time, while including the model weights would make the image even larger. Instead, the checkpoint could be stored separately in object storage and downloaded or mounted at runtime.
This keeps the Docker image smaller and makes it easier to update the model without rebuilding the entire image.