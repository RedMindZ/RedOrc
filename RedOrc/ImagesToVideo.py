import re
import os
import subprocess

imageSets = os.listdir("ProgressReports\\")
for imageSet in imageSets:
    if os.path.isfile("ProgressVideos\\" + imageSet + ".mp4"):
        os.remove("ProgressVideos\\" + imageSet + ".mp4")
    
    images = os.listdir("ProgressReports\\" + imageSet + "\\")
    if len(images) == 0:
        continue

    for path in images:
        if os.path.isdir("ProgressReports\\" + imageSet + "\\" + path):
            images.remove(path)
    
    images.sort(key=lambda name: int(re.search(r"\d+", name).group()))

    with open("ImagesToConvert.txt", "wt") as f:
        for image in images:
            f.write("file 'ProgressReports/" + imageSet + "/" + image + "'\n")
            f.write("duration 0.1\n")
        f.write("file 'ProgressReports/" + imageSet + "/" + images[-1] + "'")

    subprocess.run(["ffmpeg", "-f", "concat", "-safe", "0", "-i", "ImagesToConvert.txt", "-framerate", "5", "-pix_fmt", "yuv420p", "ProgressVideos/" + imageSet + ".mp4"])

os.remove("ImagesToConvert.txt")
