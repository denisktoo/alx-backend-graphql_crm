import os
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Define the transport
transport = RequestsHTTPTransport(url='http://localhost:8000/graphql')

seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

# Create the Client
client = Client(transport=transport, fetch_schema_from_transport=True)

# Define a query
query = gql(
   """
  query getRecentOrders($start: DateTime!) {
    allOrders(filter: { orderDateGte: $start }) {
      edges {
        node {
          numericId
          id
          customer {
            name
            email
          }
          products {
            name
          }
          totalAmount
          orderDate
        }
      }
    }
  }
  """
)

# Define variables
variables = {
    "start": seven_days_ago
}

# Execute query
result = client.execute(query, variable_values=variables)

# file path
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
# file_path = os.path.join(base_dir, "tmp", "order_reminders_log.txt")
file_path = f"{base_dir}/tmp/order_reminders_log.txt"

with open(file_path, 'a') as file:
  for edge in result['allOrders']['edges']:
      node = edge['node']
      order_id = node['numericId']
      email = node['customer']['email']
      timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      line = f"{timestamp} - Order ID: {order_id}, Customer Email: {email}\n"
      file.write(line)

print("Order reminders processed!")