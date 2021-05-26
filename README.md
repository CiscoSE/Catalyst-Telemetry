## Welcome to DNA Center Telemetry Dashboard

This small code allows you to quickly create a Grafana Dashboard that is 
fed from 2 DNA Centers that Cisco has:
- Sandbox: https://sandboxdnac.cisco.com
- Live: https://live.cisco.com

The use case behind this project is to show how easy is to integrate the 
telemetry/assurance information from DNA Center inside a customized dashboard
that a customer has.

In this file you can find the basic instructions to run the code.

## Architecture
TODO: finish

## Instructions

### Requirements

- Access to internet (to connect to the DNA Center instances).
- Docker installed (this app runs on Docker).

### Versions

This code was developed with Python 3.9 using the DNA Center SDK 
Dashboard v2.2.2 and influxdb-client v1.17.0 (InfluxDB 2.x).

### Steps

1. Clone the repository.
   ```
   git clone https://wwwin-github.cisco.com/nfitelop/DNA-Center-Telemetry
   ```

2. Go to the directory where the `docker-compose.yml` file is located, pull and
 build all images of the container:
   ```
    cd DNA-Center-Telemetry/
    docker-compose build
   ```

3. Grafana and InfluxDB will be automatically configured. Start all the 
   containers in the background (-d): 
   ```
    docker-compose up -d
   ```
   
   Note: there is a container named _influxdb_cli_ that just needs to run 
   once, this container will do all the setup work for you.
   
4. Browse to http://localhost:3000/ to open Grafana and log in using:
   - Username: admin
   - Password: admin
   It will ask for a password change, use the same passwords again.
     
5. Inside Grafana, you will see two dashboards if everything worked correctly:
   - General Health Status 
   - Hardware Health
    
    You should be able to access them and see the information from DNA Center.
       
### Cleanup

You can bring down all containers in this sample app with:
```
   docker-compose down
```

To make sure they're gone, check with:
```
   docker-compose ps
```

## License

Check the [LICENSE][LICENSE] file attached to the project to see all the 
details.

[DOCS]: ./docs
[LICENSE]: ./LICENSE.md