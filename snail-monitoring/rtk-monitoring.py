import serial
import serial.tools.list_ports
import time
import re  # For validating NMEA sentences

# Regular expression to validate NMEA sentences (e.g., start with $, end with checksum *XX)
nmea_regex = re.compile(r'^\$[A-Z]{5},.*\*[0-9A-Fa-f]{2}$')

def list_serial_ports():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        print(f"Device: {port.device}, Description: {port.description}")
    return ports

def is_nmea_message(data):
    """Check if the data is a valid NMEA sentence."""
    try:
        # Try to decode the data as ASCII text
        message = data.decode('ascii', errors='ignore').strip()
        # Validate the message against the NMEA format
        return bool(nmea_regex.match(message)), message
    except UnicodeDecodeError:
        # If decoding fails, it's not an NMEA message
        return False, None

def read_from_serial(port, baudrate=115200, timeout=1, output_file="data/serial_output.txt"):
    ser = serial.Serial(port, baudrate, timeout=timeout, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)
    
    with open(output_file, 'a') as text_file, open("binary_output.bin", 'ab') as binary_file:  # Binary file for binary data
        print(f"Reading from {port} and saving data...")

        while True:
            if ser.in_waiting > 0:
                # Read raw bytes from the serial port
                serial_data = ser.readline()

                # Check if the data contains any NMEA messages mixed with binary
                if b'$' in serial_data:
                    # Split the data into parts wherever a '$' occurs
                    parts = serial_data.split(b'$')
                    for part in parts:
                        # Reconstruct potential NMEA message
                        if part:
                            # Add back the '$' that was removed during the split
                            possible_nmea = b'$' + part
                            # Check if this part is a valid NMEA message
                            is_nmea, nmea_message = is_nmea_message(possible_nmea)
                            if is_nmea:
                                # If it's a valid NMEA message, check if it is GNGGA or GNRMC
                                if nmea_message.startswith('$GNGGA') or nmea_message.startswith('$GNRMC'):
                                    if nmea_message.startswith('$GNRMC') and nmea_message.split(",")[2] == "A":
                                        # If it's a valid NMEA message, save it as text
                                        print("NMEA Message:", nmea_message)
                                        text_file.write(nmea_message + '\n')
                                        text_file.flush()
                                    elif nmea_message.startswith('$GNGGA') and int(nmea_message.split(",")[7]) > 0:
                                        # If it's a valid NMEA message, save it as text
                                        print("NMEA Message:", nmea_message)
                                        text_file.write(nmea_message + '\n')
                                        text_file.flush()
                #             else:
                #                 # If it's not a valid NMEA message, it's probably binary
                #                 print("Binary Data:", possible_nmea)
                #                 binary_file.write(possible_nmea)
                #                 binary_file.flush()
                # else:
                #     # If no '$' is found, it's binary data
                #     print("Binary Data:", serial_data)
                #     binary_file.write(serial_data)
                #     binary_file.flush()

            time.sleep(0.1)

if __name__ == "__main__":
    ports = list_serial_ports()
    itk_port = [port.device for port in ports if "Bluetooth" not in port.description][0]
    
    try:
        read_from_serial(itk_port)
    except serial.SerialException as e:
        print(f"Error: {e}")

