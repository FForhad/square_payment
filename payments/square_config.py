from square.client import Client

# Replace these with your Square Sandbox credentials
SQUARE_ACCESS_TOKEN = "EAAAly5RUwCkpWuyX_Iv5-xmU2Zsjar3p7_YFeT3K7BSRyJqiq51B9R1XqnAnMCw"  # Access Token
SQUARE_APPLICATION_ID = "sandbox-sq0idb-4zgLtGoIhnWJMIubsLWGTw"  # Application ID
SQUARE_ENVIRONMENT = "sandbox"  # Use 'sandbox' or 'production'

# Initialize the Square Client
client = Client(
    access_token=SQUARE_ACCESS_TOKEN,
    environment=SQUARE_ENVIRONMENT,
)

# Example to access Application ID (if needed elsewhere)
APPLICATION_ID = SQUARE_APPLICATION_ID
