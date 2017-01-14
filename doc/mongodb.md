## Install as service

### Create file `mongod.cfg` with following content:
```
systemLog:
    destination: file
    path: D:\mongodb\log\mongod.log
storage:
    dbPath: D:\mongodb\data
```
### Run following command in cmd in Admin mode
`mongod --config "D:\mongodb\mongod.cfg" --install`

### Start/Stop service

`net start MongoDB`
`net stop MongoDB`