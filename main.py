'''
Author: Brendan Pratt
Organization: Pacific Northwest Seismic Network

SeisScripter - Main

Runs a bash script on every instance of a device, and writes the output to a results file.
Parameters for this program are stored in the "params.py" file. Make sure they are correct before
running the program!

Last modified: 1/2/2025
'''
import functions as funcs
import params
import paramiko as pm
import getpass
import time


def main():

    # Print welcome message:
    print("Welcome to SeisScript!\n")
    print("With great power comes minimal responsibility.\n")
    print("Brendan does not have a lawyer but still DECLARES that he will ")
    print("not be held responsible for any damage his tools cause due to the ")
    print("bad scripting of others. Make sure your bash script doesn't break stuff.\n")
    print("Now on to the program!\n\n")

    # Choose device type:
    DEVICE_TYPE = funcs.choose_device_type()
    if DEVICE_TYPE == 'TITAN-SMA' or DEVICE_TYPE == 'CENTAUR':
        REMOTE_PATH = '/home/root'
    elif DEVICE_TYPE == 'OBSIDIAN':
        REMOTE_PATH = '/root/'

    if params.TESTING:
        print(f"\nTESTING (SITE:IP file: {params.TESTING_CSV}):\n")
    elif not params.TESTING:
        print("\nPRODUCTION (SITE:IP file generated from Netbox):\n")

    print(f"Running {params.SH_SCRIPT_PATH}{params.SH_SCRIPT} on {DEVICE_TYPE}'s\n")
    print("Proceed?\n")

    if funcs.prompt_yes_or_no():
        if params.TESTING:
            print("TESTING:")
            site_ips_dict = funcs.create_dev_ip_dict_from_csv(params.TESTING_CSV)
        else:
            print("PRODUCTION:\n\n")
            # Generate dict of site:login_info from netbox, saved as csv:
            ips_csv = funcs.get_netbox_ips(DEVICE_TYPE)
            site_ips_dict = funcs.create_dev_ip_dict_from_csv(ips_csv)

        pw_chunk = getpass.getpass("Enter password chunk: \n")

        with open(params.RESULTS_PATH + params.RESULTS_CSV, 'w', newline='') as results_csv:
            # Write csv header
            if len(params.RESULTS_HEADER) == 0 or params.RESULTS_HEADER is None:
                params.RESULTS_HEADER = "Results\n"
                results_csv.write("Site Code,Results\n")
            else:
                results_csv.write("Site Code," + params.RESULTS_HEADER + "\n")

            # Start ssh client
            ssh_client = pm.SSHClient()
            ssh_client.set_missing_host_key_policy(pm.AutoAddPolicy())

            # Log into each site one at a time
            for site_code in site_ips_dict:
                time.sleep(params.DELAY)
                ip_addr = site_ips_dict[site_code][0]
                ssh_port = site_ips_dict[site_code][1]
                pw = site_code[0:2] + pw_chunk
                print()
                print(f"Connecting to {site_code}...\n")

                # TODO: Only use one try/except block
                try:
                    ssh_client.connect(ip_addr,
                                       username='root',
                                       password=pw,
                                       port=ssh_port,
                                       timeout=params.TIMEOUT)
                except:
                    error = "Could not connect to device"
                    funcs.handle_error(results_csv, site_code, error)
                    continue

                # Copy file to device:
                # TODO: Use a for loop and allow for copying multiple files
                # TODO: Create directory to copy them to
                try:
                    # TODO: Use a web socket to run local file. Use a while loop to parse sh script
                    # and run each
                    funcs.copy_file_to_device(ssh_client,
                                              params.SH_SCRIPT_PATH + params.SH_SCRIPT,
                                              REMOTE_PATH + params.SH_SCRIPT)
                    print(f"{params.SH_SCRIPT} copied to {site_code} successfully \n")
                except:
                    error = f"{params.SH_SCRIPT} failed to copy to device"
                    funcs.handle_error(results_csv, site_code, error)
                    continue

                # Run file on device:
                try:
                    results = funcs.run_linux_command(ssh_client,
                                                    f"sh {REMOTE_PATH + params.SH_SCRIPT}")
                    # Store results:
                    print(f"Successfully ran {params.SH_SCRIPT} on site {site_code}!\n")
                    print(f"{site_code}:    {results}")
                    results_csv.write(site_code + f",{results}" + "\n")
                except:
                    error = f"Failed to run {params.SH_SCRIPT}"
                    funcs.handle_error(results_csv, site_code, error)
                    continue

                # Delete file from device:
                # TODO: delete directory instead
                try:
                    funcs.run_linux_command(ssh_client,
                                            f"rm {REMOTE_PATH + params.SH_SCRIPT}")
                    print(f"{params.SH_SCRIPT} successfully deleted from")
                    print(f"{site_code}:{REMOTE_PATH}")
                except:
                    error = f"{REMOTE_PATH + params.SH_SCRIPT} NOT DELETED"
                    funcs.handle_error(results_csv, site_code, error)
                    continue

    print("\nFIN!\n")


if __name__ == main():
    main()
