import time
from paddleocr import PaddleOCRVL

print("go", flush=True)

pipeline = PaddleOCRVL(device="cpu")
print("Model loaded", flush=True)

img_path = "../../data/doc/img.jpg"

start = time.time()
print("Predicting...", flush=True)

result = pipeline.predict(img_path)

end = time.time()

print(f"Prediction took {end - start:.2f} seconds", flush=True)
print(result, flush=True)
