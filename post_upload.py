Import("env")
import subprocess
import os

def after_upload(source, target, env):
    print("Running post-upload script...")
    subprocess.run(["python3", "./src/controller.py"])

env.AddPostAction("upload", after_upload)