'''
Author: Brendan Pratt
Organization: Pacific Northwest Seismic Network

SeisScripter - Functions

This file contains functions used in the SeisScript program

Last modified: 11/27/2024
'''
import paramiko as pm
import private as priv
import csv
import requests
import re


def prompt_yes_or_no():
    '''
    Prompts user to type Y or N, returns True (Y) or False (N).
    '''
    while True:
        choice = input("(Y/N)?    ").strip().upper()

        if choice == 'Y' or choice == 'YES':
            return True
        elif choice == 'N' or choice == 'NO':
            return False
        else:
            print("Invalid choice. Please enter Y or N")
            print()


def choose_device_type():
    while True:
        print("\nSelect a device type:\n")
        print("1: TitanSMA")
        print("2: Centaur")
        print("3: Obsidian")
        print("4: Etna2")
        print()
        choice = input("I choose:    ").upper()

        if choice == '1' or choice == 'TITAN-SMA':
            return 'TITAN-SMA'
        elif choice == '2' or choice == 'CENTAUR':
            return 'CENTAUR'
        elif choice == '3' or choice == 'OBSIDIAN':
            return 'OBSIDIAN'
        else:
            print("Invalid choice. Please enter 1, 2, 3 or 4\n")


def create_dev_ip_dict_from_csv(input_csv: str) -> dict[str, str]:
    '''
    Given an input csv in format "Site Code,IP,Port", returns a dictionary with keys of site codes
    and values of a tuple with IP and ssh port.
    '''
    devices_dict = {}
    with open(input_csv, 'r') as file:
        reader = csv.reader(file)
        # Skip the header row
        next(reader)
        for row in reader:
            # Check for and prevent duplicates
            if row[0] in devices_dict:
                print("DUP! : " + row[0])
            else:
                devices_dict[row[0]] = (row[1], row[2])
    return devices_dict


def get_netbox_ips(dev_type: str,
                 token: str = priv.netbox_auth_token,
                 url: str = priv.netbox_url,
                 params: dict[str, any] = {
                     "limit": 10000
                     }
                 ) -> str:
    '''
    Queries the netbox API and generates a csv of "Station Code,IP Address,SSH Port" pairings for a
    device type and saves it as a csv. Uses Brendan's netbox authentification if none specified.
    Returns the filepath of the csv.

    # TODO: Use: # wget -qO-
    https://rachel.ess.washington.edu/netbox/export_csv.php?model=titan-sma
    '''
    output_csv: str = 'data/' + dev_type.lower() + '_ips.csv'
    auth_header = {"Authorization": "Token {0}".format(token)}
    r = requests.get(url, headers=auth_header, params=params)
    res = r.json()

    print()
    print(f"Generating {dev_type.lower()} IP dict... saved as {output_csv}")

    with open(output_csv, 'w') as my_csv:
        w = csv.writer(my_csv)
        column_names = ['Site Code', 'IP', 'Port']
        w.writerow(column_names)
        for i in res['results']:
            netbox_dev_type = i['device']['name'][-len(dev_type):]
            if i['name'] == "SSH" and netbox_dev_type == dev_type.upper():
                site = i['device']['name'].split("_", 1)[0]
                ip = i['description'].split(':')[0]
                ssh_port = i['description'].split(':')[1]

                # Check for correct formatting of IP address:
                if check_if_ipv4(ip):
                    row = site, ip, ssh_port
                    w.writerow(row)
                else:
                    print("Invalid IP Format: ", row)

            # Reset variables for next site:
            site = None
            ip = None
            ssh_port = None
            row = None

    return output_csv


def check_if_ipv4(ip_addr: str) -> bool:
    '''
    Returns True if a string fits the format of an ipv4 ip address, False if it doesn't.
    '''
    # Regex pattern for IPv4 addresses
    ipv4_pattern = r'^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    # Use re.match to check if the string matches the pattern
    match = re.match(ipv4_pattern, ip_addr)
    # If a match is found and it spans the entire string, it's a valid IPv4 address
    if match and match.span() == (0, len(ip_addr)):
        return True
    else:
        return False


def handle_error(results_csv, site_code: str, error: str) -> None:
    print("ERROR:\n")
    print(site_code + ": " + error)
    results_csv.write(site_code + "," + error + "\n")


def copy_file_to_device(remote_client: pm.SSHClient,
                        local_filepath: str,
                        remote_filepath: str) -> None:
    '''
    Copies a file to a remote device
    '''
    sftp = remote_client.open_sftp()
    sftp.put(local_filepath, remote_filepath)
    sftp.close()
    return


def run_linux_command(ssh_client: pm.SSHClient,
                command: str) -> str:
    '''
    Given a paramiko ssh client and a linux command, returns the raw output of the command.
    '''
    stdin, stdout, stderr = ssh_client.exec_command(command)
    if stderr:
        print(stderr)
    stdout.channel.set_combine_stderr(True)
    # if stderr:
    #     return stderr.read().decode()
    return stdout.read().decode()
