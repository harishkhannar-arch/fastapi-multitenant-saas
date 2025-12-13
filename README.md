# Organization Management Service

A multi-tenant backend service built with **FastAPI** and **MongoDB**. This system implements a "Database-per-Tenant" architecture where every organization gets its own dedicated collection for data isolation.

## 🏗️ Architecture Diagram
```mermaid
graph TD
    Client[Client / Frontend] -->|HTTP Request| API[FastAPI Server]
    
    subgraph Database Layer [MongoDB Cluster]
        API -->|1. Check Auth & Metadata| Master[Master DB]
        API -->|2. Route Data| OrgA[(Collection: Org_Tesla)]
        API -->|2. Route Data| OrgB[(Collection: Org_SpaceX)]
        API -->|2. Route Data| OrgC[(Collection: Org_Google)]
    end
    
    classDef database fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    class Master,OrgA,OrgB,OrgC database;