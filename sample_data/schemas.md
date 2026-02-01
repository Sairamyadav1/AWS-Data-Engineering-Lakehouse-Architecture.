# Sample Data Schema Definitions

## Bronze Layer Schema

### Raw Customer Data
```json
{
  "schema": "bronze_customer_data",
  "fields": [
    {
      "name": "customer_id",
      "type": "string",
      "description": "Unique customer identifier"
    },
    {
      "name": "first_name",
      "type": "string",
      "description": "Customer first name"
    },
    {
      "name": "last_name",
      "type": "string",
      "description": "Customer last name"
    },
    {
      "name": "email",
      "type": "string",
      "description": "Customer email address"
    },
    {
      "name": "phone",
      "type": "string",
      "description": "Customer phone number"
    },
    {
      "name": "registration_date",
      "type": "timestamp",
      "description": "Account registration timestamp"
    },
    {
      "name": "ingestion_timestamp",
      "type": "timestamp",
      "description": "Data ingestion timestamp (metadata)"
    },
    {
      "name": "ingestion_date",
      "type": "date",
      "description": "Data ingestion date partition (metadata)"
    },
    {
      "name": "source_file",
      "type": "string",
      "description": "Source file path (metadata)"
    }
  ]
}
```

### Raw Transaction Data
```json
{
  "schema": "bronze_transaction_data",
  "fields": [
    {
      "name": "transaction_id",
      "type": "string",
      "description": "Unique transaction identifier"
    },
    {
      "name": "customer_id",
      "type": "string",
      "description": "Customer identifier"
    },
    {
      "name": "product_id",
      "type": "string",
      "description": "Product identifier"
    },
    {
      "name": "transaction_date",
      "type": "timestamp",
      "description": "Transaction timestamp"
    },
    {
      "name": "amount",
      "type": "decimal(10,2)",
      "description": "Transaction amount"
    },
    {
      "name": "quantity",
      "type": "integer",
      "description": "Product quantity"
    },
    {
      "name": "status",
      "type": "string",
      "description": "Transaction status"
    },
    {
      "name": "ingestion_timestamp",
      "type": "timestamp",
      "description": "Data ingestion timestamp (metadata)"
    },
    {
      "name": "ingestion_date",
      "type": "date",
      "description": "Data ingestion date partition (metadata)"
    },
    {
      "name": "source_file",
      "type": "string",
      "description": "Source file path (metadata)"
    }
  ]
}
```

## Silver Layer Schema

### Cleansed Customer Data
```json
{
  "schema": "silver_customer_data",
  "fields": [
    {
      "name": "customer_id",
      "type": "string",
      "description": "Unique customer identifier"
    },
    {
      "name": "full_name",
      "type": "string",
      "description": "Customer full name (standardized)"
    },
    {
      "name": "email",
      "type": "string",
      "description": "Validated email address"
    },
    {
      "name": "phone",
      "type": "string",
      "description": "Standardized phone number"
    },
    {
      "name": "registration_date",
      "type": "date",
      "description": "Account registration date"
    },
    {
      "name": "customer_segment",
      "type": "string",
      "description": "Customer segment classification"
    },
    {
      "name": "processed_timestamp",
      "type": "timestamp",
      "description": "Data processing timestamp (metadata)"
    },
    {
      "name": "data_quality_flag",
      "type": "string",
      "description": "Data quality indicator (metadata)"
    },
    {
      "name": "ingestion_date",
      "type": "date",
      "description": "Partition key (metadata)"
    }
  ]
}
```

### Cleansed Transaction Data
```json
{
  "schema": "silver_transaction_data",
  "fields": [
    {
      "name": "transaction_id",
      "type": "string",
      "description": "Unique transaction identifier"
    },
    {
      "name": "customer_id",
      "type": "string",
      "description": "Customer identifier"
    },
    {
      "name": "product_id",
      "type": "string",
      "description": "Product identifier"
    },
    {
      "name": "transaction_date",
      "type": "date",
      "description": "Transaction date"
    },
    {
      "name": "transaction_timestamp",
      "type": "timestamp",
      "description": "Transaction timestamp"
    },
    {
      "name": "amount",
      "type": "decimal(10,2)",
      "description": "Transaction amount"
    },
    {
      "name": "quantity",
      "type": "integer",
      "description": "Product quantity"
    },
    {
      "name": "status",
      "type": "string",
      "description": "Standardized transaction status"
    },
    {
      "name": "revenue",
      "type": "decimal(10,2)",
      "description": "Calculated revenue"
    },
    {
      "name": "processed_timestamp",
      "type": "timestamp",
      "description": "Data processing timestamp (metadata)"
    },
    {
      "name": "data_quality_flag",
      "type": "string",
      "description": "Data quality indicator (metadata)"
    },
    {
      "name": "ingestion_date",
      "type": "date",
      "description": "Partition key (metadata)"
    }
  ]
}
```

## Gold Layer Schema

### Customer Analytics
```json
{
  "schema": "gold_customer_analytics",
  "fields": [
    {
      "name": "customer_id",
      "type": "string",
      "description": "Unique customer identifier"
    },
    {
      "name": "full_name",
      "type": "string",
      "description": "Customer full name"
    },
    {
      "name": "total_transactions",
      "type": "bigint",
      "description": "Total number of transactions"
    },
    {
      "name": "total_revenue",
      "type": "decimal(10,2)",
      "description": "Total revenue generated"
    },
    {
      "name": "avg_transaction_value",
      "type": "decimal(10,2)",
      "description": "Average transaction value"
    },
    {
      "name": "first_purchase_date",
      "type": "date",
      "description": "Date of first purchase"
    },
    {
      "name": "last_purchase_date",
      "type": "date",
      "description": "Date of last purchase"
    },
    {
      "name": "customer_lifetime_value",
      "type": "decimal(10,2)",
      "description": "Customer lifetime value"
    },
    {
      "name": "customer_segment",
      "type": "string",
      "description": "Customer segment"
    },
    {
      "name": "aggregation_timestamp",
      "type": "timestamp",
      "description": "Aggregation timestamp (metadata)"
    }
  ]
}
```

### Daily Sales Aggregates
```json
{
  "schema": "gold_daily_sales",
  "fields": [
    {
      "name": "transaction_date",
      "type": "date",
      "description": "Transaction date"
    },
    {
      "name": "total_transactions",
      "type": "bigint",
      "description": "Total number of transactions"
    },
    {
      "name": "total_revenue",
      "type": "decimal(10,2)",
      "description": "Total revenue"
    },
    {
      "name": "unique_customers",
      "type": "bigint",
      "description": "Number of unique customers"
    },
    {
      "name": "avg_transaction_value",
      "type": "decimal(10,2)",
      "description": "Average transaction value"
    },
    {
      "name": "total_quantity_sold",
      "type": "bigint",
      "description": "Total quantity of products sold"
    },
    {
      "name": "aggregation_timestamp",
      "type": "timestamp",
      "description": "Aggregation timestamp (metadata)"
    }
  ]
}
```
