# Synthetic Data Generator

## Overview
This script generates 1000 realistic shipments distributed across all Indian states and different workflow stages.

## Usage

### Step 1: Run the generator
```powershell
cd D:\National-Logistics-Control-Tower\National-Logistics-Control-Tower
python create_synthetic_data.py
```

### Step 2: Restart your Streamlit app
After generation completes, restart your Streamlit application to load the new data.

## Distribution
The script creates shipments in the following distribution:
- **15%** (150) - CREATED (waiting for manager approval)
- **10%** (100) - MANAGER_APPROVED (waiting for supervisor)
- **5%** (50) - SUPERVISOR_APPROVED (ready for dispatch)
- **20%** (200) - IN_TRANSIT (dispatched to receiver)
- **15%** (150) - RECEIVER_ACKNOWLEDGED (acknowledged by receiver)
- **10%** (100) - WAREHOUSE_INTAKE (at warehouse)
- **15%** (150) - OUT_FOR_DELIVERY (last mile delivery)
- **10%** (100) - DELIVERED (completed)

## Features
- Realistic weight distribution (mostly 1-20kg, some up to 50kg)
- 70% NORMAL delivery, 30% EXPRESS
- Random source/destination across all Indian states
- Proper event sourcing transitions through all states
- Appends to existing data (doesn't overwrite)

## Notes
- Generation takes approximately 2-3 minutes
- Data is saved to: `data/logs/shipments.jsonl`
- All shipments use proper event sourcing
- Can be run multiple times to add more data
