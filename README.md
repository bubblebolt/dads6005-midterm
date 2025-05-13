# 🛍️ BoBoShop: Real-Time Data Streaming & Analytics System

[🚀 **Live Dashboard**](https://boltshops.streamlit.app/?classId=ed1339f6-5561-43f2-b8e5-cd134adcc7d0&assignmentId=45fe71b2-3cfc-4e50-b2f1-64dcf5e1dd1d&submissionId=d867db4f-e866-d942-61cb-e6584c05e6b7) | [🎥 **Tutorial Reference**](https://www.youtube.com/watch?v=pzDXRNcmyfY)

---

## 📚 Project Overview

This project demonstrates a **real-time data streaming and analytics system** simulating an e-commerce environment.  
It integrates:

- **Apache Kafka** for real-time message streaming
- **ksqlDB** for stream processing
- **Apache Pinot** for real-time OLAP queries
- **Streamlit** for live dashboard visualization

> **Goal:** Simulate user behaviors and transactions, process real-time data streams, and visualize insights dynamically.

---

## 📈 System Architecture Diagram

![System Architecture](https://raw.githubusercontent.com/bubblebolt/dads6005-midterm/main/Pics/Flowchart.png)

---

## ⚙️ System Components

### 🔹 1. Data Sources
- **PageViews**: Simulated pageview events (Kafka Connect Datagen)
- **Users**: Simulated user registration profiles (Kafka Connect Datagen)
- **Orders**: Simulated order transactions (Python script)

### 🔹 2. Kafka System Setup
- 5 partitions per topic
- 3 brokers setup for high availability
- 8 topics in total (raw, cleaned, and aggregated data)
- Schema Registry integration
- Kafka Connect for data ingestion automation

### 🔹 3. ksqlDB Stream Processing
- Data Cleaning: Rescale viewtime and convert registertime format
- Aggregations: Join Orders and Users, group by product type
- Windowed Analysis:
  - Tumbling Window (1-hour fixed)
  - Hopping Window (1-hour size, 30-min advance)
  - Session Window (10-minute inactivity timeout)
- Testing Correctness: Via input.json, output.json, and SQL validation

### 🔹 4. Real-time OLAP with Apache Pinot
- Ingested 3 real-time tables: Pageviews, Users, Orders
- Queries executed:
  - Average sales by U.S. state
  - Pageview counts per user and page
  - Total sales by product type

### 🔹 5. Real-Time Dashboard (Streamlit)
- Real-time metrics and visualizations:
  - 📈 Average sales per product type (Metric)
  - 📄 Customer order behavior (Dataframe)
  - 🥧 Total sales distribution by product (Pie Chart)
  - 👀 Pageviews per user (Selectable Multiselect Graph)
  - 🗺️ Average purchase per state (Choropleth Map)

- **Bonus Features**:
  - Auto-refresh every 5 seconds
  - Product image display in dashboard

---

## 🖼️ Example Dashboard View

![Dashboard Example](https://raw.githubusercontent.com/bubblebolt/dads6005-midterm/main/Pics/Picture1.png)

---

## 🧰 Tech Stack

- **Apache Kafka** (Confluent Platform)
- **Kafka Connect** (Data Generator Source Connector)
- **ksqlDB** (Real-time stream processing)
- **Apache Pinot** (Real-time OLAP datastore)
- **Streamlit** (Interactive dashboard)
- **Python** (Data simulation and dashboard development)
- **Plotly Express** (Interactive charts)

---

## 🏆 Key Achievements

- Designed and implemented an end-to-end **real-time data pipeline**.
- Developed multiple **windowed analytics** using Tumbling, Hopping, and Session windows.
- Built a **dynamic, auto-refreshing dashboard** to monitor real-time business insights.
