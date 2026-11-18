# SOAP API Public Fetch

This Flask application calls the public InterSystems SOAP Demonstration Service's `AddInteger` operation through its WSDL.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

The service runs at `http://127.0.0.1:5000`.

## Try the routes

```powershell
curl.exe "http://127.0.0.1:5000/add?arg1=7&arg2=35"

# PowerShell's --% tells it to pass the JSON quotation marks through to curl.exe.
curl.exe --% -X POST http://127.0.0.1:5000/add -H Content-Type:application/json -d {"arg1":7,"arg2":35}
```

Both values must be whole numbers from -10,000 through 10,000.

## Test

```powershell
pytest
```
