import os
from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# file path
base_dir = os.path.dirname(os.path.dirname(__file__))
# file_path = os.path.join(base_dir, "tmp", "crm_heartbeat_log.txt")
file_path = f"{base_dir}/tmp/crm_heartbeat_log.txt"

def log_crm_heartbeat():
    # Define the transport
    transport = RequestsHTTPTransport(url='http://localhost:8000/graphql')

    # Create the Client
    client = Client(transport=transport, fetch_schema_from_transport=True)

    # Define a query
    query = gql(
    """
    query {
      hello
    }
    """
    )

    # Execute query
    try:
        result = client.execute(query)
        print(f"GraphQL response: {result}")
    except Exception as e:
        print(f"GraphQL query failed: {e}")

    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")

    with open(file_path, "a") as file:
        file.write(f"{timestamp} CRM is alive\n")

if __name__ == '__main__':
    log_crm_heartbeat()
