# Physical Protection System (PPS) Camera Feed

## Description and Purpose

This is a Flask server designed to stream two MP4s:

1. `/vid/door_closed.mp4` (default)
2. `/vid/door_open.mp4` (streamed for a set time)

The server has the ability to receive API calls to:

1. Switch the default `door_closed.mp4` feed to `door_open.mp4` when `/switch` is called.
2. Freeze the stream when `/frz` is called

## Installation Instructions 

**Python Version:** `3.8.10`

**APT Extras:**
```bash
sudo apt-get update && sudo apt-get install libgl1 ffmpeg libsm6 libxext6 -y
```

**PIP Packages:**
```bash
pip install requirements.txt
```

## Directory Structure

`vid` - folder containing two .mp4 files

## Starting the Server

```bash
python3 stream.py
```
