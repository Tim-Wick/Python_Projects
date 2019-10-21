# This program takes an IP address and mask and returns the subnet address, first address, last address,
# and broadcast address

import re
import time


def check_ip(ip):
    valid_ip = re.match(r"^([1-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\."
                        r"([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\."
                        r"([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\."
                        r"([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])$", ip)
    # regex matches values of four groups of digits separated with periods with the first group being 1-255
    # and last three being 0-255

    if valid_ip:
        return True
    else:
        return False


def pre_fix_to_decimal(pre_fix_convert):
    if pre_fix_convert == 32:
        return_values = {"Mask": "255.255.255.255", "Interesting Octet": 4}
        return return_values
    # grabs a 32 bit pre-fix and auto returns all 255's. There might be a way to algorithmically do this.

    number_of_255_octets = int(pre_fix_convert/8)  # gets the number of octets that are 255
    host_bits = 8 - (pre_fix_convert % 8)  # gets the number of bits that will be "0" in the first non 255 octet
    decimal_mask_list = []  # sets up decimal mask list

    for i in range(number_of_255_octets):  # loops through octets that need to be 255.
        decimal_mask_list.append("255.")

    decimal_mask_list.append(str(256 - (2**host_bits)))
    # first subtracts 256 from 2^host bits to get the decimal value found from the subnet bits
    # then appends onto the decimal mask list

    while len(decimal_mask_list) < 4:
        decimal_mask_list.append(".0")  # appends .0 to fill out rest of mask

    decimal_mask = "".join(decimal_mask_list)  # creates string out of mask list to return so it matches user input
    interesting_octet_pre = number_of_255_octets + 1
    return_values = {"Mask": decimal_mask, "Interesting Octet": interesting_octet_pre}
    return return_values


# Function takes in  a subnet mask in decimal format as a string and returns true if it is valid, else returns false
def check_subnet_mask(mask):
    if mask == "255.255.255.255":
        # There might be a better way to work this
        return_values = {"Result": True, "Mask": mask, "Interesting Octet": 4}
        return return_values
    mask_int = mask.split(".")  # splits mask into a list
    if len(mask_int) != 4 or mask_int[0] == "0":  # returns false if the mask doesn't have 4 octets or the first octet is 0
        return_values = {"Result": False}
        return return_values
    valid_list = [0, 128, 192, 224, 240, 248, 252, 254]  # sets up list of valid options
    mask_int = [int(i) for i in mask_int]  # turns the given string to ints to avoid calculating the int of each octet
    for i in range(4):  # we know the list is 4 after the check above, this loops through it
        if mask_int[i] == 255:  # if the octet is 255 we can continue
            continue
        elif mask_int[i] in valid_list and sum(mask_int[(i+1):]) == 0:
            # checks if the number is in the list of valid values if so checks if the rest of the values sum to 0
            # eg, once we have a value other than 255, the rest need to be 0
            interesting_octet_dec = i + 1
            return_values = {"Result": True, "Mask": mask, "Interesting Octet": interesting_octet_dec}
            return return_values
        else:
            return_values = {"Result": False}
            return return_values


print("Welcome to the IP calculator! I eat IPs and Subnet Masks and return the network address, first host address,"
      " last host address, and broadcast address!")

while True:

    ip_address = input("Enter an IP address: ")
    while (ip_address != "q") and (not check_ip(ip_address)):
        print("That doesn't look like a valid IP, try again!")
        ip_address = input("Enter an IP address or enter 'q' to quit: ")

    if ip_address == "q":
        break

    subnet_mask = input("Valid IP! Enter a subnet mask in decimal or pre-fix starting with a '/'."
                        " Or enter 'q' to quit: ")

    while subnet_mask != "q":
        subnet_mask_checked = check_subnet_mask(subnet_mask)
        if subnet_mask_checked["Result"]:
            subnet_mask = subnet_mask_checked
            break
        elif subnet_mask[0] == "/":
            pre_fix = int(subnet_mask[1:])
            if 0 < pre_fix < 33:
                subnet_mask = pre_fix_to_decimal(pre_fix)
                break
            else:
                print("That doesn't look like a valid mask, try again!")
                subnet_mask = input("Enter a subnet mask in decimal or pre-fix starting with a '/'. "
                                    "Or enter 'q' to restart: ")
        else:
            print("That doesn't look like a valid mask, try again!")
            subnet_mask = input("Enter a subnet mask in decimal or pre-fix starting with a '/'."
                                " Or enter 'q' to restart: ")

    if subnet_mask == "q":
        break

    print("Valid mask! Calculating addresses...\n")
    print("Given IP address: " + ip_address)
    print("Given subnet mask: " + subnet_mask["Mask"] + "\n")

    # subnet mask is dictionary of mask as a string and interesting octet as an int
    ip_address = ip_address.split(".")
    subnet_mask_split = subnet_mask["Mask"].split(".")
    interesting_octet = subnet_mask["Interesting Octet"]
    interesting_octet_ip = interesting_octet - 1  # needs to be minus one since ip list will count from 0
    magic_number = 256 - int(subnet_mask_split[interesting_octet_ip])
    subnet_number = int(int(ip_address[interesting_octet_ip]) / magic_number)

    network_address = magic_number * subnet_number
    broadcast_address = (magic_number * (subnet_number + 1)) - 1

    if interesting_octet == 4:
        network_ip = ip_address.copy()
        network_ip[interesting_octet_ip] = str(network_address)
        first_ip = ip_address.copy()
        first_ip[interesting_octet_ip] = str(network_address + 1)

        broadcast_ip = ip_address.copy()
        broadcast_ip[interesting_octet_ip] = str(broadcast_address)
        last_ip = ip_address.copy()
        last_ip[interesting_octet_ip] = str(broadcast_address - 1)
    else:
        base_ip = ip_address[:interesting_octet_ip]
        fill_in_octets = 3 - interesting_octet

        network_ip = base_ip.copy()
        network_ip.append(str(network_address))
        for j in range(fill_in_octets):
            network_ip.append("0")
        network_ip.append("0")
        first_ip = network_ip.copy()
        first_ip[3] = "1"

        broadcast_ip = base_ip.copy()
        broadcast_ip.append(str(broadcast_address))
        for k in range(fill_in_octets):
            broadcast_ip.append("255")
        broadcast_ip.append("255")
        last_ip = broadcast_ip.copy()
        last_ip[3] = "254"

    print("Network address: " + ".".join(network_ip))
    print("First host address: " + ".".join(first_ip))
    print("Last host address: " + ".".join(last_ip))
    print("Broadcast address: " + ".".join(broadcast_ip) + "\n")

    print("Nom Nom! Give me another!\n")

print("Thanks for playing! Bye!")
time.sleep(3)
