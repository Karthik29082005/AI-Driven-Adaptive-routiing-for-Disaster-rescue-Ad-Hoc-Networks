# 🚁 AI-Driven Disaster Rescue Routing System

An intelligent disaster response management system that uses AI and reinforcement learning to optimize rescue unit routing and deployment during emergencies. The system automatically generates alerts, assigns rescue units, and uses Q-Learning algorithms to find optimal routes in real-time.

## 📋 Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Key Components](#key-components)
- [Default Credentials](#default-credentials)
- [Database Schema](#database-schema)
- [System Architecture](#system-architecture)

## ✨ Features

### 🤖 Automatic Operations
- **Auto-Alert Generation**: Automatically generates disaster alerts within selected state boundaries every 30-60 seconds
- **Auto-Deployment**: Automatically assigns and deploys rescue units to alerts without manual intervention
- **Smart Routing**: Units automatically route to alert locations, then to hospitals (ambulances) or shelters (other units)

### 🧠 AI & Machine Learning
- **Q-Learning Router**: Reinforcement learning-based routing system that learns optimal paths
- **Dynamic Rerouting**: Automatically reroutes units when failures occur using learned Q-values
- **Performance Tracking**: Tracks and visualizes AI performance metrics over time

### 🗺️ Interactive Mapping
- **Live Map Visualization**: Real-time map showing all rescue units, alerts, hospitals, and shelters
- **Unit Tracking**: Visual tracking of unit movements and status (idle, moving, arrived, failed)
- **State-Based Operations**: Operates within randomly selected Indian states with realistic geographic boundaries

### 👥 Role-Based Access
- **Admin Dashboard**: Full control panel with alerts, team management, reports, and AI performance monitoring
- **Member Dashboard**: Team member view with personal operations map and nearby alerts
- **User Management**: Admin can add, edit, and manage team members

### 📊 Reporting & Analytics
- **Operational Reports**: View and download reports for alerts, assignments, failures, and AI performance
- **RL Performance Graphs**: Visualize Q-Learning improvement over time
- **Database Logging**: All operations logged to SQLite database for analysis

### 🚨 Alert Management
- **Multi-Severity Alerts**: Low, Moderate, and High severity levels
- **Automatic Assignment**: Up to 4 units automatically assigned per alert
- **Real-time Notifications**: Instant notifications for new alerts and unit status changes

## 🛠 Technology Stack

- **Frontend**: Streamlit
- **Mapping**: Folium, streamlit-folium
- **Graph Processing**: NetworkX
- **Data Processing**: Pandas
- **Visualization**: Matplotlib
- **Database**: SQLite
- **AI/ML**: Custom Q-Learning implementation

## 📦 Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Steps

1. **Clone or navigate to the project directory**
   ```bash
   cd ai_disaster_rescue
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the database**
   ```bash
   python init_db.py
   ```

4. **Run the application**
   ```bash
   streamlit run src/app.py
   ```

5. **Access the application**
   - The app will open in your default browser at `http://localhost:8501`
   - If not, navigate to the URL shown in the terminal

## 🚀 Usage

### Starting the System

1. **Login**: Use default credentials (see [Default Credentials](#default-credentials))
2. **Automatic Mode**: The system automatically starts generating alerts and deploying units
3. **Monitor Operations**: Watch real-time operations on the interactive map

### Admin Features

- **Live Map**: View all units, alerts, and their movements
- **Alerts & Deployment**: Manually create alerts or view automatic deployments
- **AI Performance**: Monitor Q-Learning router performance and improvements
- **Team Management**: Add, edit, or remove team members
- **Reports**: Generate and download operational reports

### Member Features

- **My Operation Map**: View assigned operations and nearby units
- **Alerts Near Me**: See personal alerts and notifications

## 📁 Project Structure

```
ai_disaster_rescue/
├── database/
│   └── users.db                 # SQLite database
├── models/                      # Unit type icons/images
│   ├── ambulance.png
│   ├── drone.png
│   ├── fire_truck.png
│   ├── police.png
│   ├── van.png
│   ├── hospital.png
│   ├── shelter.png
│   └── ... (broken state variants)
├── src/
│   ├── app.py                   # Main application entry point
│   ├── login.py                 # Authentication system
│   ├── auth.py                  # Authorization utilities
│   ├── admin_dashboard.py       # Admin interface
│   ├── member_dashboard.py      # Member interface
│   ├── auto_system.py           # Automatic alert generation & deployment
│   ├── env_demo.py              # Environment simulation (states, nodes, graph)
│   ├── districts.py             # State/district data and utilities
│   ├── ui_map.py                # Map rendering and controls
│   ├── ui_alert.py              # Alert UI and assignment logic
│   ├── movement.py              # Unit movement and routing
│   ├── failures.py              # Failure handling
│   ├── rl_graph.py              # RL performance visualization
│   ├── admin_user_mgmt.py       # User management
│   ├── db_logs.py               # Database logging utilities
│   ├── routing/
│   │   ├── __init__.py
│   │   └── qlearning.py         # Q-Learning router implementation
│   └── style.css                # Custom styling
├── init_db.py                   # Database initialization script
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🔑 Key Components

### Q-Learning Router (`routing/qlearning.py`)
- Implements reinforcement learning for optimal path finding
- Learns from routing decisions and improves over time
- Automatically reroutes units when failures occur
- Tracks performance metrics (time taken, improvement percentage)

### Automatic System (`auto_system.py`)
- Generates random alerts within state boundaries
- Automatically deploys available units to alerts
- Handles unit arrivals and routes to final destinations (hospitals/shelters)
- Manages alert lifecycle (active for 3 minutes, cleanup after 5 minutes)

### Environment (`env_demo.py`)
- Creates a MANET (Mobile Ad-hoc Network) graph over Indian states
- Generates rescue units (drones, ambulances, vans, fire trucks, police)
- Connects nodes based on distance thresholds
- Provides shortest path routing using NetworkX

### Movement System (`movement.py`)
- Manages unit positions and status
- Handles route assignment and execution
- Updates unit positions in real-time
- Tracks unit states: idle, moving, arrived, failed

## 🔐 Default Credentials

After running `init_db.py`, the following default accounts are created:

### Admin Account
- **Username**: `admin@gmail.com`
- **Password**: `admin123`
- **Role**: Admin

### Team Member Account
- **Username**: `team1@gmail.com`
- **Password**: `team123`
- **Role**: Member

> **Note**: Change these credentials in production environments!

## 🗄️ Database Schema

The system uses SQLite with the following tables:

### `users`
- `id`: Primary key
- `username`: Unique username (email)
- `password`: SHA-256 hashed password
- `role`: User role (admin/member)
- `full_name`: User's full name
- `phone`: Contact number

### `alerts`
- `id`: Primary key
- `latitude`: Alert latitude
- `longitude`: Alert longitude
- `severity`: Alert severity (Low/Moderate/High)
- `timestamp`: Creation timestamp

### `assignments`
- `id`: Primary key
- `unit_id`: Assigned unit identifier
- `assigned_to`: Team member email
- `alert_id`: Associated alert ID
- `timestamp`: Assignment timestamp

### `failures`
- `id`: Primary key
- `unit_id`: Failed unit identifier
- `reason`: Failure reason
- `latitude`: Failure location latitude
- `longitude`: Failure location longitude
- `timestamp`: Failure timestamp

### `rl_metrics`
- `id`: Primary key
- `episode`: Episode number
- `time_taken`: Routing time in seconds
- `improvement`: Improvement percentage vs previous route
- `timestamp`: Metric timestamp

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Admin Panel  │  │Member Panel  │  │  Login/Auth  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
┌───────▼──────┐ ┌──────▼──────┐ ┌─────▼──────┐
│ Auto System  │ │ Q-Learning  │ │  Movement  │
│  (Alerts &   │ │   Router    │ │  System    │
│ Deployment)  │ │             │ │            │
└───────┬──────┘ └──────┬──────┘ └─────┬──────┘
        │               │               │
        └───────────────┼───────────────┘
                        │
                ┌───────▼───────┐
                │ DemoEnv       │
                │ (State/Graph) │
                └───────┬───────┘
                        │
                ┌───────▼───────┐
                │   SQLite DB   │
                │  (Logging)    │
                └───────────────┘
```

## 📝 Notes

- The system operates in **automatic mode** by default, generating alerts and deploying units automatically
- Units are automatically assigned to team members when deployed
- The Q-Learning router improves routing decisions over time as it encounters more scenarios
- All operations are logged to the database for analysis and reporting
- The system uses Indian state boundaries for realistic geographic simulation

## 🤝 Contributing

This is a demonstration project for AI-driven disaster rescue routing. Feel free to extend it with:
- Additional rescue unit types
- More sophisticated RL algorithms
- Integration with real mapping APIs
- Multi-state operations
- Advanced failure recovery mechanisms

## 📄 License

This project is provided as-is for educational and demonstration purposes.

---

**Built with ❤️ for efficient disaster response management**

