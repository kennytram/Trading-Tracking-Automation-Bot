import cv2
import os
import gc
import re
import numpy as np
from google.cloud import vision
from google.oauth2 import service_account
from urllib.request import urlopen

# ================= CONFIG =================
TEMPLATE_DIR = "templates"

ORB_FEATURES = 3000
ORB_DISTANCE_THRESHOLD = 60
MIN_FINAL_SCORE = 0.15

ORB_WEIGHT = 0.7
COLOR_WEIGHT = 0.3

CREDENTIALS = service_account.Credentials.from_service_account_file(
    os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
)
CLIENT = vision.ImageAnnotatorClient()

EXCLUDED_KEYWORDS = [
    'ID:', 
    'Return', 
    'F1 Intro', 
    'F Check Announcements', 
    'R Refresh',
    'Trade Commission',
    'Co-op Fluctuation',
    'Price',
    'Local Price Remote Price Friend Price'
    'Z Local Price Remote Price Friend Price C',
    'Bag',
    'Bag*',
    'Co-op',
    '>',
    '▲ 0',
    '▲',
    'Go to Purchase',
    'Stock *',
    'R Share',
    'Space Confirm Sale',
]

# regex patterns for invalid lines (126k, 1M)
INVALID_PATTERNS = [
    re.compile(r'^\d+[KM]$', re.IGNORECASE)
]

# Not allowing these symbols in player names
FORBIDDEN_SYMBOLS = r"!@#\$%\^&\*\(\)\+_=\{\[\]\}\\\|:;\"'<,>\./\?"

# Collect valid player names
VALID_NAME_REGEX = re.compile(
    rf"^(?!.*[{FORBIDDEN_SYMBOLS}])(?=.*[A-Za-z\u4e00-\u9fff]).+$"
)

class ImageProcessor:
    def __init__(self, 
                 nfeatures=ORB_FEATURES, 
                 norm_type=cv2.NORM_HAMMING, 
                 cross_check=True, 
                 content=None):
        
        # Matcher initialization
        self.orb = cv2.ORB_create(nfeatures)
        self.bf = cv2.BFMatcher(norm_type, cross_check)
        self.templates = {}

        self.load_templates()

        # Scanner initialization
        self.content = content
        self.image = None
        self.url = None
        self.ocr_text = ""

        
        
    def load_templates(self, dir=TEMPLATE_DIR):
        for file in os.listdir(dir):
            if file.lower().endswith(".png") or file.lower().endswith(".jpg"):
                path = os.path.join(dir, file)
                img = cv2.imread(path, cv2.IMREAD_UNCHANGED)

                if img is None or img.shape[2] != 4:
                    continue

                name = os.path.splitext(file)[0]

                bgr = img[:, :, :3]
                alpha = img[:, :, 3]

                mask = (alpha > 0).astype("uint8") * 255
                gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

                kp, des = self.orb.detectAndCompute(gray, mask)

                if des is None:
                    continue

                hist = self.compute_hsv_histogram(bgr, mask)

                self.templates[name] = {
                    "kp": kp,
                    "des": des,
                    "hist": hist
                }

    def compute_hsv_histogram(self, bgr_img, mask=None):
        hsv = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2HSV)

        hist = cv2.calcHist(
            [hsv],
            [0, 1],
            mask,
            [50, 60],
            [0, 180, 0, 256]
        )

        cv2.normalize(hist, hist)
        return hist
    
    def crop_regions(self, image):
        h, w = image.shape[:2]

        return {
            # "top": image[: h // 2, :],
            "left": image[:, : w // 2],
            "center": image[h // 4 : 3 * h // 4, w // 4 : 3 * w // 4],
            "top_left": image[: h // 2, : w // 2],
        }
    
    def detect_item_from_image(self, image_bgr):

        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        kp_s, des_s = self.orb.detectAndCompute(gray, None)

        if des_s is None:
            return None, 0

        screenshot_hist = self.compute_hsv_histogram(image_bgr)

        best_item = None
        best_score = 0

        for name, data in self.templates.items():
            matches = self.bf.match(des_s, data["des"])
            matches = sorted(matches, key=lambda m: m.distance)

            good_matches = [m for m in matches if m.distance < ORB_DISTANCE_THRESHOLD]
            if not good_matches:
                continue

            orb_score = len(good_matches) / len(data["des"])

            color_score = cv2.compareHist(
                screenshot_hist,
                data["hist"],
                cv2.HISTCMP_CORREL
            )

            final_score = (ORB_WEIGHT * orb_score) + (COLOR_WEIGHT * color_score)

            if final_score > best_score:
                best_score = final_score
                best_item = name

        if best_score >= MIN_FINAL_SCORE:
            return best_item, best_score

        return None, best_score
    
    async def read_image_from_url(self):
        try:
            resp = urlopen(self.url)
            image_bytes = resp.read()
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return image
        except Exception as e:
            print(f"[ERROR] Failed to read image from URL: {e}")
            return None
        
    def detect_item_with_regions(self, image):
        # image = cv2.imread(image_path)
        # image = await self.read_image_from_url(image_path)

        if image is None:
            return None, 0, None
        results = []

        for region_name, region_img in self.crop_regions(image).items():
            item, score = self.detect_item_from_image(region_img)
            if item:
                results.append((item, score, region_name))

        if not results:
            return None, 0, None

        # best_item, best_score, best_region = max(results, key=lambda x: x[1])

        # temp implementation
        # Prefer non-left regions if possible
        non_left_results = [r for r in results if r[2] != "left"]

        if non_left_results:
            best_item, best_score, best_region = max(non_left_results, key=lambda x: x[1])
        else:
            # fallback to left if it's the only region with a score
            best_item, best_score, best_region = max(results, key=lambda x: x[1])


        return best_item, best_score, best_region
    
    def get_matched_item(self, image_path):
        item = self.detect_item_with_regions(image_path)[0]
        return item
    
    # Scanner methods for OCR
    def get_image_url(self):
        return self.url
    
    def set_image_url(self, url):
        self.url = url

    def get_content(self):
        return self.content
    
    def set_content(self, content):
        self.content = content
    
    async def scan_image_for_market_data(self):
        self.image = vision.Image(content=self.content)
        self.image.source.image_uri = self.url
        player_names = []
        percentages = []
        
        response = CLIENT.text_detection(image=self.image)

        self.ocr_text = response.text_annotations[0].description

        lines = [l.strip() for l in self.ocr_text.splitlines() if l.strip()]

        for i, line in enumerate(lines):
            if any(kw in line for kw in EXCLUDED_KEYWORDS):
                continue
            if any(p.match(line) for p in INVALID_PATTERNS):
                continue
            # temp: skip single uppercase letters
            if len(line) == 1 and line.isupper():
                continue
            if VALID_NAME_REGEX.match(line):
                player_names.append(line)

        percent_regex = re.compile(r"^[\+\-]?(\d+)%")
        for line in lines:
            match = percent_regex.match(line)
            if match:
                value = int(match.group(1))
                # If line starts with '-', set to 0
                if line.startswith('-'):
                    value = 0
                percentages.append(value)

        # Signals that it is a local price screenshot with only one percentage
        if not percentages:
            # Must have an empty space in front of the +/- symbol
            percent_regex = re.compile(r"(?<=\s)[\+\-](\d+)%")
            for line in lines:
                match = percent_regex.search(line)
                if match:
                    value = int(match.group(1))
                    matched_str = match.group(0)
                    if matched_str.startswith('-'):
                        value = 0
                    percentages.append(value)

        pairs = []
        # Pair names and percentages in order
        if len(percentages) == 1 and len(player_names) > 1:
            # Only one percentage found, likely a local price screenshot
            pass
        else:
            # Reverse both lists to pair from the end in case of misalignment
            pairs = list(zip(player_names[::-1], percentages[::-1]))
            # Reverse back to original order
            pairs = pairs[::-1]
        
        self.reset_garbage()

        # return data. If data is empty, return percentage to indicate it's local
        return pairs if pairs else ["", percentages[0]]
    
    def reset_garbage(self):
        self.content = None
        # release large image object
        del self.image  
        # force garbage collection
        gc.collect()  
