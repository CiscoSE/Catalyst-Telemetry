## Welcome to DNA Telemetry Dashboard

This small piece of code allows you to quickly create a few Grafana Dashboards 
that are fed from different DNA elements such as DNA Center and vManage 
(SD-WAN).

The DNA Centers used are:
- Sandbox: https://sandboxdnac.cisco.com
- Live: https://live.cisco.com

The vManage used is:
- SD-WAN demo: https://sdwandemo.cisco.com

The use case behind this project is to show how easy is to integrate the 
telemetry/assurance information from DNA elements inside a customized 
dashboard that a customer might have.

You can find the basic instructions to run the code in the section 
[Instructions](#Instructions).

## Architecture

The following image illustrates the architecture:

![DNA Center Architecture](/images/DNA_DNAC_Telemetry.png)

![SD-WAN Architecture](/images/DNA_SD-WAN_Telemetry.png)

It uses:
- Collector: Python-based script.
- InfluxDB 2.0: time series database.
- Grafana: dashboard.

## Screenshots

Containers in steady state:
![Containers in steady state](/images/containers_steady.png)

DNA Center General Health Status Dashboard:
![DNA Center General Health Status Dashboard](/images/dnac_general_health_status.png)

DNA Center Hardware Health Dashboard
![DNA Center Hardware Health Dashboard](/images/dnac_hardware_health.png)

SD-WAN General Health Status Dashboard:
![SD-WAN General Health Status Dashboard](/images/sdwan_general_health_status.png)


## Instructions

### Requirements

- Access to internet (to connect to the DNA Center & SD-WAN instances).
- Docker installed (this app runs on Docker).

### Versions

This code has been developed and tested with Python 3.8, using the DNA Center 
SDK Dashboard v2.4.9 and influxdb-client v1.28.0 (InfluxDB 2.0).

### Steps

1. Clone the repository.
   ```
   git clone https://wwwin-github.cisco.com/nfitelop/DNA-Telemetry
   ```

2. Go to the directory where the `docker-compose.yml` file is located, pull and
 build all images of the container:
   ```
    cd DNA-Telemetry/
    docker-compose build
   ```

3. Start all the containers in the background (-d). Grafana and InfluxDB will 
   be automatically configured. 
   ```
    docker-compose up -d
   ```
   
   **Note:** there is a container named _influxdb_cli_ that just needs to run 
   once, this container will do all the setup work for you and afterwards 
   it will stop.
   
   **Note 2:** the containers _influxdb_cli_ and _collector_ need the database 
   to be up and running, that takes some time, you might see both 
   containers restarting a few times before they can do their job.

   
4. Browse to http://localhost:3000/ to open Grafana and log in using:
   - **Username**: admin
   - **Password**: admin
   
   It will ask for a password change, use the same passwords again.
   

5. Inside Grafana, click on the _Search_ button on the left-side menu, you 
   will see two dashboards if everything worked correctly:
   - DNAC - General Health Status 
   - DNAC - Hardware Health
   - SD-WAN - General Health Status
   
   You should be able to access them and see the information from the 
   different sources.
       
### Cleanup

You can bring down all containers in this sample app with:
```
   docker-compose down
```

To make sure they're gone, check with:
```
   docker-compose ps
```

## Caveats

In the dashboard _SD-WAN - General Health Status_ the panel _Transport Health_ might be empty sometimes.
The data in this panel is obtained in vManage every hour, so the refresh rate is 1 hour. If the dashboard time range is configured
to less than 1 hour it will be empty. If you **want to see data** configure the dashboard **time range to at least 1 hour**. 
If you want multiple data points 3 hours is a good setting, but it requires the collector to be running at least for that amount
of time.

## Troubleshooting

A common error is that the DNA Center has an invalid certificate, please check that SSL verfication is turned off
to avoid any issues.

## License

Check the [LICENSE][LICENSE] file attached to the project to see all the 
details.

[LICENSE]: ./LICENSE.md