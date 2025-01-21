"""
Copyright (c) 2025 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

import os
import time

import dnacentersdk
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.client.write_api import WritePrecision

from sdwan_helper import RestApiLib
from setup import influxdb_setup

# Get configuration data.
load_dotenv()
influxdb_host = os.getenv('INFLUX_HOST')
influxdb_port = os.getenv('INFLUX_PORT')
influxdb_catalystcenterbucket = os.getenv('INFLUX_CATALYSTCENTERBUCKET')
influxdb_sdwanbucket = os.getenv('INFLUX_SDWANBUCKET')
influxdb_token = os.getenv('INFLUX_TOKEN')
influxdb_org = os.getenv('INFLUX_ORG')
collector_interval = int(os.getenv('COLLECTOR_INTERVAL'))
catalystcenter_sandbox_url = os.getenv('CATALYSTCENTER_SANDBOX_URL')
catalystcenter_sandbox_user = os.getenv('CATALYSTCENTER_SANDBOX_USER')
catalystcenter_sandbox_password = os.getenv('CATALYSTCENTER_SANDBOX_PASSWORD')
catalystcenter_live_url = os.getenv('CATALYSTCENTER_LIVE_URL')
catalystcenter_live_user = os.getenv('CATALYSTCENTER_LIVE_USER')
catalystcenter_live_password = os.getenv('CATALYSTCENTER_LIVE_PASSWORD')
sdwan_sandbox_host = os.getenv('SDWAN_SANDBOX_HOST')
sdwan_sandbox_port = os.getenv('SDWAN_SANDBOX_PORT')
sdwan_sandbox_user = os.getenv('SDWAN_SANDBOX_USER')
sdwan_sandbox_password = os.getenv('SDWAN_SANDBOX_PASSWORD')

# Setup InfluxDB.
influxdb_setup()
client = InfluxDBClient(
    url="http://" + influxdb_host + ":" + str(influxdb_port),
    token=influxdb_token)

# Setup Catalyst Center Sandbox.
catalystcenter_sandbox = dnacentersdk.DNACenterAPI(
    base_url=catalystcenter_sandbox_url,
    username=catalystcenter_sandbox_user,
    password=catalystcenter_sandbox_password,
    verify=False)

# Setup Catalyst Center Live.
catalystcenter_live = dnacentersdk.DNACenterAPI(
    base_url=catalystcenter_live_url,
    username=catalystcenter_live_user,
    password=catalystcenter_live_password,
    verify=False)

# Setup SD-WAN Sandbox.
sdwan_session = RestApiLib(sdwan_sandbox_host,
                           sdwan_sandbox_port,
                           sdwan_sandbox_user,
                           sdwan_sandbox_password)

while True:
    # InfluxDB write API.
    write_api = client.write_api(write_options=SYNCHRONOUS)

    """ Catalyst Center section """
    # Client health.
    response = catalystcenter_live.clients.get_overall_client_health().response
    for score in response[0]['scoreDetail']:
        score_category = score['scoreCategory']['value']
        score_client_count = score['clientCount']
        score_value = score['scoreValue']

        # Save to influxdb
        data = "client_health_general,score_category=" + score_category + \
               " score_value=" + str(score_value)
        write_api.write(influxdb_catalystcenterbucket, influxdb_org, data)
        data = "client_health_general,score_category=" + score_category + \
               " client_count=" + str(score_client_count)
        write_api.write(influxdb_catalystcenterbucket, influxdb_org, data)
        try:
            for category in score['scoreList']:
                category_type = category['scoreCategory']['value']
                client_count = category['clientCount']

                data = "client_health_detailed,score_category=" + \
                       score_category + ",type=" + category_type + \
                       " client_count=" + str(client_count)
                write_api.write(influxdb_catalystcenterbucket, influxdb_org, data)
        except:
            pass

    devices = catalystcenter_sandbox.devices. \
        get_device_list(family="Switches and Hubs").response
    for device in devices:
        device_details = catalystcenter_sandbox. \
            devices.get_device_detail(identifier="uuid",
                                      search_by=device.id).response
        cpu = device_details.cpu
        overall_health = device_details.overallHealth
        device_name = device.nwDeviceName

        data = "cpu,host=" + device.id + ",device_name=" + device.hostname + \
               " cpu_used=" + str(cpu)
        write_api.write(influxdb_catalystcenterbucket, influxdb_org, data)
        data = "overall_health,host=" + device.id + ",device_name=" + \
               device.hostname + " overall_health=" + str(overall_health)
        write_api.write(influxdb_catalystcenterbucket, influxdb_org, data)

    """ SD-WAN Section """
    # Get the control connections statistics (vBond, vSmart, vEdge).
    control_connections_summary = sdwan_session. \
        get_request("network/connectionssummary")

    items = control_connections_summary.json()['data']
    # For each type (vSmart, WAN Edge and vBond) get the data and save it.
    for item in items:
        name = item["name"].replace(" ", "\ ")
        down_devices = 0
        for status in item["statusList"]:
            down_devices += status["count"]

            data = "connections_summary,name=" + name + \
                   ",status=" + status["status"] + " count=" + \
                   str(down_devices)
            write_api.write(influxdb_sdwanbucket, influxdb_org, data)

        data = "connections_summary,name=" + name + ",status=" \
               + "up" + " count=" + str(item["count"] - down_devices)
        write_api.write(influxdb_sdwanbucket, influxdb_org, data)

    # Get vManage statistics.
    vmanage_summary = sdwan_session. \
        get_request("clusterManagement/health/summary").json()['data']
    for item in vmanage_summary:
        name = item["name"].replace(" ", "\ ")
        down_devices = 0
        for status in item["statusList"]:
            down_devices += status["count"]
            data = "connections_summary,name=" + name + \
                   ",status=" + status["status"] + " count=" + \
                   str(down_devices)
            write_api.write(influxdb_sdwanbucket, influxdb_org, data)

        data = "connections_summary,name=" + name + ",status=" \
               + "up" + " count=" + str(item["count"] - down_devices)
        write_api.write(influxdb_sdwanbucket, influxdb_org, data)

    # Get Device Control status.
    device_control_summary = sdwan_session. \
        get_request("device/control/count").json()['data'][0]
    for status in device_control_summary["statusList"]:
        name = status["name"].replace(" ", "\ ")
        data = "device_control_summary,name=" + name + \
               ",status=" + status["status"] + " count=" + \
               str(status["count"])
        write_api.write(influxdb_sdwanbucket, influxdb_org, data)

    # Get Site Health data.
    site_health_summary = sdwan_session. \
        get_request("device/bfd/sites/summary").json()['data'][0]
    for status in site_health_summary["statusList"]:
        name = status["name"].replace(" ", "\ ")
        data = "site_health,name=" + name + \
               ",status=" + status["status"] + " count=" + \
               str(status["count"])
        write_api.write(influxdb_sdwanbucket, influxdb_org, data)

    # Get Hardware Health data.
    hardware_health_summary = sdwan_session. \
        get_request("device/hardwarehealth/summary").json()['data'][0]

    for item in hardware_health_summary["statusList"]:
        data = "hardware_health,status=" + item["name"] + \
               " count=" + str(item["count"])
        write_api.write(influxdb_sdwanbucket, influxdb_org, data)

    # Get Transport Summary
    query = '{"query":{"condition":"AND","rules":[{"value":["1"],' \
            '"field":"entry_time","type":"date","operator":"last_n_hours"}]}}'
    transport_summary = sdwan_session. \
        get_request("statistics/approute/transport/summary/loss_percentage"
                    "?limit=5&query=" + query).json()["data"]

    for transport in transport_summary:
        data = "transport_health,transport=" + transport["color"] + \
               " loss_percentage=" + str(transport["loss_percentage"]) + " " \
               + str(transport["entry_time"])
        write_api.write(influxdb_sdwanbucket,
                        influxdb_org,
                        data,
                        write_precision=WritePrecision.MS)

    # Get Applications Summary.
    query = '{"query":{"condition":"AND","rules":[{"value":["1"],' \
            '"field":"entry_time","type":"date","operator":"last_n_hours"}]}}'
    applications_summary = sdwan_session. \
        get_request("statistics/dpi/applications/summary?"
                    "limit=10&query=" + query).json()["data"]

    for application in applications_summary:
        data = "application_summary,application=" + \
               application["application"] + " octets=" + \
               str(application["octets"])
        write_api.write(influxdb_sdwanbucket, influxdb_org, data)

    # Get Transport Interface Distribution.
    transport_distribution = sdwan_session. \
        get_request("device/tlocutil").json()["data"]

    for interface in transport_distribution:
        percentageDistribution = interface["percentageDistribution"]. \
            replace(" ", "\ ")
        data = "transport_distribution,name=" + \
               interface["name"] + ",percentage_distribution=" + \
               percentageDistribution + " value=" + \
               str(interface["value"])
        write_api.write(influxdb_sdwanbucket, influxdb_org, data)

    # Pause the script for x seconds, represents the polling interval.
    time.sleep(collector_interval)
