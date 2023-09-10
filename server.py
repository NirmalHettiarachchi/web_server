import socket
import os
import json
from subprocess import Popen, PIPE

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
PORT = 2728
RESOURCE_DIR = "htdocs"
PHP_SUPPORTED_EXTENSIONS = ["php", "html"]
FORMAT = "utf-8"

# Function to handle each client connection
def handle_client(connection, client_address):
    try:
        data = connection.recv(4096).decode(FORMAT)
        print(data)

        if len(data):
            req_header_details = get_req_header_details(data) # Get header details from received data
            status_details = get_status_details(req_header_details["resource_path"]) # Get the status 
            
            #Get the byte version of the resource if available. If not this returns the 404.html
            resource = fetch_resource(**req_header_details, **status_details) 
            response = create_response(req_header_details["protocol"], status_details, resource) # Create the new response by combining headers with resource data

            connection.send(response)
            connection.close()

    except Exception as error:
        print(f"Error: {error}")
    
    print("Client disconnected...")

# Function to parse request header details
def get_req_header_details(data):
    request_line = data.split('\r\n')[0]
    method, resource_path, protocol = request_line.split()
    parameters = {}

    #In case of a GET request, the parameteres can be derived from the resource path
    if method == "GET":
        resource_path += "?"
        query_string = resource_path.split("?")[1]
        resource_path = resource_path.split("?")[0]
    #In case of a POST requesr, the parameters are stored at the bottom
    else:
        query_string = data.splitlines()[-1]

    parameters = parse_parameters_from_path(query_string) # Return the quesry_string as a dictionary
    resource_path = decide_resource_file_path(resource_path) # If there isn't a resource path specified, it will be set to "resource_path/index.html"
    resource_path = resource_path.replace("//", "/")

    return {
        "method": method,
        "resource_path": resource_path[1:],  # To avoid getting a "/" at the start of the resource path
        "protocol": protocol,
        "parameters": parameters
    }

# Function to determine the resource file path
def decide_resource_file_path(resource_path):
    # Ensure that the resource_path is in a default format
    if not resource_path.count("."):
        index_file = "index.php" if os.path.exists(f"{RESOURCE_DIR}/{resource_path}/index.php") else "index.html"
        return f"{resource_path}/{index_file}"
    
    return resource_path

# Function to parse parameters from the query string
def parse_parameters_from_path(path):
    # Parse parameters from the query string
    parameters = {}
    if path.count("="):
        for single_query in path.split("&"):
            variable, value = single_query.split("=")
            parameters[variable] = value

    return parameters

# Function to get status details (response headers)
def get_status_details(resource_path):
    status_details = {"status_code": 0, "message": "NULL"}

    if os.path.exists(f"./{RESOURCE_DIR}/{resource_path}"):
        status_details["status_code"] = 200
        status_details["message"] = "OK"
    else:
        status_details["status_code"] = 404
        status_details["message"] = "Not Found"
    
    return status_details

# Function to fetch the requested resource
def fetch_resource(**kwargs):
    method = kwargs["method"]
    path = kwargs["resource_path"]
    parameters = kwargs["parameters"]

    if kwargs["status_code"] == 404:
        with open(f"./{RESOURCE_DIR}/404.html", "rb") as resource:
            return resource.read()

    if path.split(".")[-1] in PHP_SUPPORTED_EXTENSIONS:
        output = fetch_php_output(method, path, parameters)
        return output
    else:
        with open(f"./{RESOURCE_DIR}/{path}", "rb") as resource:
            return resource.read()

# Function to fetch output from a PHP script
def fetch_php_output(method, resource_path, parameters):
    payload = json.dumps({
        "method": method,
        "path": resource_path,
        "parameters": parameters,
    })

    # Passing the metadata to the wrapper
    process = Popen(["php", f"./{RESOURCE_DIR}/wrapper.php", payload], stdout=PIPE, cwd="./")
    (output, error) = process.communicate()
    process.wait()
    print(output.decode(FORMAT))
    
    return output

# Function to create the HTTP response
def create_response(protocol, status_details, resource):
    response = f"{protocol} {status_details['status_code']} {status_details['message']}".encode(FORMAT) + b'\r\n'
    response += b"Content-Type: text/html\r\n"
    response += b"\r\n"
    
    if status_details["status_code"] == 200:
        response += resource
    else:
        response += resource

    return response

# Function to start the server
def main():
    print(f"Server running on port {PORT}")
    server_socket.bind(('', PORT))
    server_socket.listen(1)
    while True:
        connection, client_address = server_socket.accept()
        handle_client(connection, client_address)

if __name__ == "__main__":
    main()
