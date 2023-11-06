Import("env")
import subprocess

def after_upload(source, target, env):
    print("Running post-upload script...")
    subprocess.run(["python3", "/src/serial.py"])

env.AddPostAction("upload", after_upload)