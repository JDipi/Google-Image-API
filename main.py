import requests, lxml, re, json, urllib.request
from bs4 import BeautifulSoup
from flask import Flask, request
from flask_cors import CORS

# Thanks to toasty for doing all the flask routes

# CREDIT: https://replit.com/@DimitryZub1/Scrape-and-Download-Google-Images-with-Python#main.py

app = Flask(__name__)
CORS(app)

headers = {
    "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36"
}


@app.route("/")
def hello():
    return "hi daddy"


@app.route("/images/<query>&limit=<lim>")
def get(query, lim):
  #  max limit is 100
    images = []

    params = {
        "q": query,
        "tbm": "isch",
        "hl": "en",
        "ijn": "0"
    }

    html = requests.get("https://www.google.com/search",
                        params=params,
                        headers=headers,
                        timeout=30)
    soup = BeautifulSoup(html.text, 'lxml')

    all_script_tags = soup.select('script')

    matched_images_data = ''.join(
        re.findall(r"AF_initDataCallback\(([^<]+)\);",
                   str(all_script_tags)))

    matched_images_data_fix = json.dumps(matched_images_data)
    matched_images_data_json = json.loads(matched_images_data_fix)

    matched_google_image_data = re.findall(
        r'\[\"GRID_STATE0\",null,\[\[1,\[0,\".*?\",(.*),\"All\",',
        matched_images_data_json)

    matched_google_images_thumbnails = ', '.join(
        re.findall(
            r'\[\"(https\:\/\/encrypted-tbn0\.gstatic\.com\/images\?.*?)\",\d+,\d+\]',
            str(matched_google_image_data))).split(', ')

    # removing previously matched thumbnails for easier full resolution image matches.
    removed_matched_google_images_thumbnails = re.sub(
        r'\[\"(https\:\/\/encrypted-tbn0\.gstatic\.com\/images\?.*?)\",\d+,\d+\]',
        '', str(matched_google_image_data))

    matched_google_full_resolution_images = re.findall(
        r"(?:'|,),\[\"(https:|http.*?)\",\d+,\d+\]",
        removed_matched_google_images_thumbnails)

    for index, fixed_full_res_image in enumerate(matched_google_full_resolution_images):

      original_size_img_not_fixed = bytes(
      fixed_full_res_image, 'ascii').decode('unicode-escape')
      original_size_img = bytes(original_size_img_not_fixed, 'ascii').decode('unicode-escape')

      if lim:
        if index < int(lim):
          images.append(original_size_img)
        else:
          break
      else:
        images.append(original_size_img)
        
    res = app.response_class(response=json.dumps(images),
                             mimetype="application/json")
    return res


app.run("0.0.0.0")
