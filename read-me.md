# SCS2205 Computer Networks I: Simple Python Web Server

This is a simple Python web server that can handle HTTP GET and POST requests and also supports both PHP and HTML files.

## Prerequisites

Before running the server, make sure you have the following dependencies installed:

- Python 3
- PHP

## Usage

- Start the server by running the following command after navigating into the project directory:
```
python web_server.py
```
The server will start listening on the port 2728 (default).

- Place the HTML and PHP files in the `htdocs` directory. You can organize your files into subdirectories as well.

- Access the web server from your browser by navigating to `http://localhost:2728/`.

## Supported File Types

By default, the server supports HTML and PHP file types. 

## Server Details

- The server parses HTTP requests, extracts request headers and handles GET and POST requests.
- It serves HTML and PHP files from the `htdocs` directory.
- If a requested resource is not found, it returns a 404 error page.



