import os
import subprocess

if os.path.isfile("ProgressVideo.mp4"):
    os.remove("ProgressVideo.mp4")

images = os.listdir("ProgressReports")
images.sort(key=lambda name: int(name[name.index("Step") + 4:name.index("Index")]))

with open("ImagesToConvert.txt", "wt") as f:
    for image in images:
        f.write("file 'ProgressReports/" + image + "'\n")
        f.write("duration 0.02\n")
    f.write("file 'ProgressReports/" + images[-1] + "'")

subprocess.run(["ffmpeg", "-f", "concat", "-i", "ImagesToConvert.txt", "-framerate", "5", "-pix_fmt", "yuv420p", "ProgressVideo.mp4"])
os.remove("ImagesToConvert.txt")
