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
    cd cd DNA-Center-Telemetry/
    docker-compose build
   ```

4. Grafana and InfluxDB need to be configured once, start InfluxDB and Grafana 
   containers in the background (-d): 
   ```
    docker-compose up -d grafana influxdb
   ```
5. Browse to http://localhost:8086 to open InfluxDB, click on _Get Started_, 
   use the 
   following values:
   - Username: demo
   - Password: demo1234!
   - Initial Organization Name: devnet
   - Initial Bucket Name: telemetry
   
   Click on continue, afterwards click on _Configure Later_. Go to  _Data_ 
   on the left-side menu, navigate to the _Tokens_ section, click on 
   _demo's Token_, copy the token.
   
6. Go the project folder and navigate inside `app_code`, rename the file 
   `credentials_sample.yaml` to `credentials.yaml`
   
7. Open the file `credentials.yaml` and change the following line:
   ```
   influxdb_token: 'ADD YOUR TOKEN HERE'
   ```
   Paste the token you just copied there.

8. Browse to http://localhost:3000/ to open Grafana and log in using:
   - Username: admin
   - Password: admin
   It will ask for a password change, use the same passwords again.
     
9. Inside Grafana navigate using the left-side menu to _Settings > Data 
   Sources_, once opened click on _Add data source_. Search for InfluxDB 
   and select it.
   
10. Leave all as per default values except:
   - Query Language: Flux
   - URL:  
   - InfluxDB Details:
     - Organization: devnet
     - Token: paste the token you obtained in step #5.
     - Default Bucket: telemetry
   Click on _Save & Test_.






2. Configure the environment variables with the API key. Locate the file in
   the root of the project called: `docker_sample.env`.
   Rename this file to `docker.env` and add your API key in the line
   `MERAKI_DASHBOARD_API_KEY`. The file should look like this:
  
   ```
    CELERY_BROKER_URL=redis://redis:6379
    CELERY_RESULT_BACKEND=redis://redis:6379
    MERAKI_DASHBOARD_API_KEY=YOUR_API_KEY_HERE
   ```

3. Go to the directory where the `docker-compose.yml` file is located, pull and
 build all images of the container:
   ```
    cd meraki-switches-configurator/
    docker-compose build
   ```

4. Start all the containers in the background
   ```
    docker-compose up -d
   ```

5. To check on the state of the containers, run:
   ```
    docker-compose ps
   ```

6. Observe the API and celery worker logs:
   ```
    docker-compose logs -f app worker
   ```

7. Open the url <localhost:8080>, if you followed all the steps correctly
   the website will be shown.


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