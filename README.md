# EasyGUIApi

This is a simple Python application that provides a JSON server with an interface to configure the response JSON and authentication type.

## Features

-   Enter JSON response data.
-   Start and stop the server with a button.

## Requirements

-   Python 3.x

## Dependencies

PyQt6
Flask
pyjwt

## Setup

1. Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
python main.py
```

## Usage

Enter the JSON response data.
Click the 'Enable' button to start the server.
Access the server at http://localhost:4000.
Click the 'Disable' button to stop the server.
