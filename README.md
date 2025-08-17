# 📘 GraphQL CRM with Django

This project is a **GraphQL-based CRM API** built with **Django + Graphene**, implementing core GraphQL concepts such as queries, mutations, Relay Nodes, filters, and schema design.
It also includes a **database seeding script** using Django ORM (`get_or_create`), allowing pre-population of Customers, Products, and Orders.

---

## 🚀 Features

* **GraphQL API** with `graphene-django`
* **Relay Node Interface** for global IDs
* **Filtering support** with `django-filter`
* **GraphQL Mutations** for Customers, Products, and Orders
* **Django ORM Seeding Script** (`seed_db.py`)

---

## 📖 Concepts Applied

### 1. **GraphQL Queries & Mutations**

* Queries allow fetching **customers, products, and orders**.
* Mutations enable **creating customers, products, and orders**.
* Example mutation to create a customer:

  ```graphql
  mutation {
    createCustomer(input: { name: "Alice", email: "alice@example.com", phone: "+1234567890" }) {
      customer {
        id
        name
        email
        phone
      }
      message
    }
  }
  ```

---

### 2. **Relay & Node Interface**

* Implemented **Relay global IDs** for GraphQL nodes.
* Enables consistent object fetching across the schema.
* Example query fetching a customer by global ID:

  ```graphql
  query {
    node(id: "Q3VzdG9tZXJUeXBlOjE=") {
      id
      ... on CustomerType {
        name
        email
      }
    }
  }
  ```

---

### 3. **GraphQL Filtering**

* Integrated `django-filter` for searching/filtering data.
* Example: Query all customers filtered by name:

  ```graphql
  query {
    allCustomers(name: "Alice") {
      edges {
        node {
          id
          name
          email
        }
      }
    }
  }
  ```

---

### 4. **Django ORM Seeding**

* A **seeding script (`seed_db.py`)** initializes the database with:

  * Customers (Alice, Bob, Carol)
  * Products (Laptop, Tablet)
  * Orders (Alice’s order with products)
* Uses `get_or_create` for **idempotency** (avoids duplicates).
* Example: creating an order for Alice:

  ```graphql
  mutation {
    createOrder(input: { customerId: "Q3VzdG9tZXJUeXBlOjE=", productIds: ["UHJvZHVjdFR5cGU6MQ==", "UHJvZHVjdFR5cGU6Mg=="] }) {
      order {
        id
        orderDate
        products {
          name
          price
        }
      }
      message
    }
  }
  ```

---

### 5. **Django ORM `get_or_create`**

* Ensures objects are only created if they don’t exist.
* Prevents duplication when seeding or testing mutations.
* Applied for **customers, products, and orders**.

---

## ✅ Example Workflow

1. Create and apply migrations:
   ```bash
   python manage.py makemigrations crm
   python manage.py migrate
   ```

2. Seed database:

   ```bash
   python seed_db.py
   ```
3. Run server:

   ```bash
   python manage.py runserver
   ```
4. Access GraphQL API:
   [http://localhost:8000/graphql/](http://localhost:8000/graphql/)

---