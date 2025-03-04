#!/bin/bash

# Run the deep fund with the specified configuration file
# Usage: ./run_deep_fund.sh [config_file]

# Set default config file if not provided
CONFIG_FILE=${1:-"src/config/default_config.yaml"}

# Check if the config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Config file '$CONFIG_FILE' not found."
    exit 1
fi

# Run the deep fund
echo "Running Deep Fund with config: $CONFIG_FILE"
python src/main.py --config "$CONFIG_FILE" 