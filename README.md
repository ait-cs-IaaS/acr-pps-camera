# Configure

## Adapt name mapping
Open name_mapping.yml and change the mapping of video-file to first and lastname


## Run videos

### Change video of ENTERING employee
```
curl -X POST localhost:5000/video/in/gregor
```

### Change video of LEAVING employee
```
curl -X POST localhost:5000/video/out/gregor
```

### Change to NO-SIGNAL
```
curl -X POST localhost:5000/video/extra/breach
```