#!/usr/bin/env python3
"""
This small piece of code expands the Catalyst Center SDK with a new ap detail report.

Copyright (c) 2025 Cisco and/or its affiliates.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

# Import for CSV
import csv
# Import OS
import os
# Import the system
import sys
# Datetime package import
from datetime import datetime

# Catalyst Center SDK import
from dnacentersdk import DNACenterAPI, ApiError, api
# Dotenv package for environment variables
from dotenv import load_dotenv, find_dotenv


def main() -> None:
    """
    This function generates a report with more details that Catalyst Center knows about an AP,
    and creates a csv report with it.

    :return: nothing.
    """
    # Create a DNACenterAPI connection object. It loads the credentials and settings from the variables.env file.
    dnac = api.DNACenterAPI(verify=False)

    # Max value for limit is 200
    limit = 200
    # Offset is the value used to gather the offset + limit next entries
    offset = 1
    # Start with 201 as a value so the while enters, then update it to the real thing
    total_count = 0

    # Variable to store the data
    aps_simple = []
    # Keep only the necessary columns and remove the rest
    columns_to_keep = ['id', 'hostname', 'type', 'macAddress', 'apEthernetMacAddress', 'serialNumber',
                       'associatedWlcIp', 'managementIpAddress', 'reachabilityStatus']

    # One response may not contain all devices, iterate over pages using offset
    while True:
        # Call the API asking for the clients
        response = dnac.devices.get_device_list(limit=limit, offset=offset, family="Unified AP")
        aps = response['response']
        total_count += len(aps)
        offset += limit

        for ap in aps:
            aps_simple.append({key: ap[key] for key in columns_to_keep})

        if len(aps) < limit:
            break

    # Keep only the necessary columns and remove the rest
    columns_to_keep = ['primaryControllerName', 'primaryIpAddress', 'secondaryControllerName', 'secondaryIpAddress',
                       'tertiaryControllerName', 'tertiaryIpAddress']

    # Once all devices are gathered, get for each device the primary/secondary/tertiary WLCs
    for ap in aps_simple:
        ap_details = dnac.wireless.get_access_point_configuration(ap['apEthernetMacAddress'])
        ap.update({key: ap_details[key] for key in columns_to_keep})

    # Create report
    current_datetime = datetime.now()
    print(str(current_datetime) + " - Finished querying data, saving results to report.")
    print_to_csv(aps_simple, os.getenv("OUTPUT_FILENAME"))


def print_to_csv(report: list, filename: str) -> None:
    """
    This function prints into a csv file a report with the list given.
    Expects a list of dicts with the data. Extracts the keys
    from the first row and prints them as headers.

    :param report: a list of a list (or a matrix) with the data.
    :param filename: the filename of the output file.

    :return: nothing.
    """

    try:
        with open(filename, mode='w+', newline='') as file:
            file_writer = csv.writer(file, delimiter=',', quotechar='"',
                                     quoting=csv.QUOTE_MINIMAL)
            # Writing headers of CSV file
            header = report[0].keys()
            file_writer.writerow(header)

            for line in report:
                file_writer.writerow(line.values())
    except PermissionError as perm_err:
        if perm_err.errno == 13:
            message = "The output file cannot be modified, make sure it is closed."
            print(message)
        else:
            print(str(perm_err))


if __name__ == "__main__":
    """
    This function executes the main function if this script is executed.
    """

    try:
        load_dotenv(find_dotenv())
        main()
    except ApiError as err:
        print(err)
    sys.exit()
