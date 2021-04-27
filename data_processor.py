import pprint
import os
import cognitive_face as CF

from time import sleep
import csv

from PIL import Image
import PIL.ExifTags as ExifTags

from datetime import datetime as dt


def getRectangle(faceDictionary):  # Extract the positional coordinates of faces .
    rect = faceDictionary["faceRectangle"]
    left = rect["left"]
    top = rect["top"]
    right = left + rect["height"]
    bottom = top + rect["width"]
    return ((left, top), (right, bottom))


def get_image_data(fname):
    # get lat and lon
    # #reffering https://news.mynavi.jp/article/zeropython-42/
    def conv_deg(v):
        d = float(v[0])
        m = float(v[1])
        s = float(v[2])
        return d + (m / 60.0) + (s / 3600.0)

    im = Image.open(fname)
    exif = {ExifTags.TAGS[k]: v for k, v in im._getexif().items() if k in ExifTags.TAGS}

    try:
        gps_tags = exif["GPSInfo"]
        gps = {ExifTags.GPSTAGS.get(t, t): gps_tags[t] for t in gps_tags}

        lat = conv_deg(gps["GPSLatitude"])
        lat_ref = gps["GPSLatitudeRef"]
        if lat_ref != "N":
            lat = 0 - lat
        lon = conv_deg(gps["GPSLongitude"])
        lon_ref = gps["GPSLongitudeRef"]
        if lon_ref != "E":
            lon = 0 - lon
    except KeyError:
        lat, lon = 0, 0

    # Get 35mm equiv.
    thirtyfivemm_equivalent = exif["FocalLengthIn35mmFilm"]

    # Get time of shooting
    tdatetime = dt.strptime(exif["DateTimeOriginal"], "%Y:%m:%d %H:%M:%S")

    yobi_list = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    day = yobi_list[tdatetime.weekday()]

    shooting_date = "{}/{}/{}".format(
        str(tdatetime.year), str(tdatetime.month), str(tdatetime.day)
    )

    shooting_hour_and_minute = str(tdatetime.hour) + ":" + str(tdatetime.minute)
    shooting_hour_and_minute = "{}:{}".format(
        str(tdatetime.hour), str(tdatetime.minute)
    )
    shooting_hour = str(tdatetime.hour)

    time_number = 0
    if tdatetime.hour == 11 or tdatetime.hour == 12 or tdatetime.hour == 13:
        time_number = 1
    if tdatetime.hour == 14 or tdatetime.hour == 15 or tdatetime.hour == 16:
        time_number = 2
    if tdatetime.hour == 17 or tdatetime.hour == 18 or tdatetime.hour == 19:
        time_number = 3

    img_data = {
        "lat": lat,
        "lon": lon,
        "thirtyfivemm_equivalent": thirtyfivemm_equivalent,
        "day": day,
        "shooting_date": shooting_date,
        "shooting_hour_and_minute": shooting_hour_and_minute,
        "shooting_hour": shooting_hour,
        "time_number": time_number,
        "image_width": im.size[0],
    }

    return img_data


KEY = "????"  # Enter the apikey you got, or just one line in key.txt
BASE_URL = "https://japaneast.api.cognitive.microsoft.com/face/v1.0"

if KEY == "????":
    with open("key.txt") as f:
        for line in f:
            KEY = line

CF.Key.set(KEY)
CF.BaseUrl.set(BASE_URL)

images = os.listdir("./img")
images = [
    image
    for image in images
    if image[-3:].lower() == "jpg" or image[-4:].lower() == "jpeg"
]  # select only jpeg image

facedata_list = [
    [
        "imagename",
        "order",
        "age",
        "gender",
        "anger",
        "comtempt",
        "disgust",
        "fear",
        "happiness",
        "neutral",
        "sadness",
        "surprise",
        "emotion",
        "Lat",
        "Lon",
        "Occupied Width",
        "Focal Length In 35mm Film",
        "day",
        "date",
        "hour:minute",
        "hour",
        "time num",
        "distance",
    ]
]

print("Target image:", images)
for image in images:
    img_url = "img/" + image
    faces = CF.face.detect(
        img_url, face_id=True, landmarks=True, attributes="age,gender,emotion"
    )

    img_data = get_image_data(img_url)

    # read image
    print("\nAnalysing:", img_url)
    reading_img = Image.open(str(img_url))

    counter = 0
    for face in faces:
        pos = getRectangle(face)
        img = reading_img.crop(
            (pos[0][0], pos[0][1], pos[1][0], pos[1][1])
        )  # (left, upper, right, lower)
        imagename = "{}_{}.jpg".format(
            os.path.splitext(os.path.basename(image))[0], str(counter + 1)
        )  # output faces named as "imagename_order"
        img.save(str("output/" + imagename), quality=95)

        occupied_width = pos[1][0] - pos[0][0]

        face_width = {
            "male": 161.9,
            "female": 153.8,
        }  # reffering to "Japanese Body: Health and Physical Data Collection"

        distance = (
            img_data["thirtyfivemm_equivalent"]
            * face_width[face["faceAttributes"]["gender"]]
            * img_data["image_width"]
            / occupied_width
            / 35
        )

        facedata_list.append(
            [
                image.rstrip(".jpg .JPG"),
                counter + 1,  # first number is "1"
                face["faceAttributes"]["age"],
                face["faceAttributes"]["gender"],
                face["faceAttributes"]["emotion"]["anger"],
                face["faceAttributes"]["emotion"]["contempt"],
                face["faceAttributes"]["emotion"]["disgust"],
                face["faceAttributes"]["emotion"]["fear"],
                face["faceAttributes"]["emotion"]["happiness"],
                face["faceAttributes"]["emotion"]["neutral"],
                face["faceAttributes"]["emotion"]["sadness"],
                face["faceAttributes"]["emotion"]["surprise"],
                max(
                    face["faceAttributes"]["emotion"],
                    key=face["faceAttributes"]["emotion"].get,
                ),  # emotion
                img_data["lat"],  # Lat
                img_data["lon"],  # Lon
                occupied_width,  # Imagesize
                img_data["thirtyfivemm_equivalent"],  # 35mm換算焦点距離
                img_data["day"],  # 曜日
                img_data["shooting_date"],  # 日付
                img_data["shooting_hour_and_minute"],  # 時分
                img_data["shooting_hour"],  # 時
                img_data["time_number"],  # 時間帯番号
                distance,
            ]
        )
        counter += 1

    if counter == 0:  # If no faces are detected
        facedata_list.append(
            [
                image.rstrip(".jpg .JPG"),
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                img_data["lat"],  # Lat
                img_data["lon"],  # Lon
                "",  # Imagesize
                img_data["thirtyfivemm_equivalent"],  # 35mm換算焦点距離
                img_data["day"],  # 曜日
                img_data["shooting_date"],  # 日付
                img_data["shooting_hour_and_minute"],  # 時分
                img_data["shooting_hour"],  # 時
                img_data["time_number"],  # 時間帯番号
                "",
            ]
        )

    print("Finished analysing {}".format(image))
    sleep(3.2)

# Set character encoding to Shift_JIS.
with open("facedata.csv", "w", encoding="Shift_jis") as f:
    writer = csv.writer(f, lineterminator="\n")
    writer.writerows(facedata_list)
