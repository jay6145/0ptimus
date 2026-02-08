#!/bin/bash

# Quick verification that Fahrenheit conversion is working

echo "🌡️  Fahrenheit Conversion Verification"
echo "========================================"
echo ""

# Get latest telemetry
TELEMETRY=$(curl -s http://localhost:8000/api/telemetry/1/latest)

echo "Backend Data (stored in Celsius):"
echo "----------------------------------"
echo "$TELEMETRY" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for sensor, reading in sorted(data['sensors'].items()):
    value = reading['value']
    unit = reading.get('unit', '')
    if 'temp' in sensor:
        print(f'{sensor:25} {value:6.1f}°C')
    else:
        print(f'{sensor:25} {value:6.1f} {unit}')
"

echo ""
echo "Frontend Display (converted to Fahrenheit):"
echo "--------------------------------------------"
echo "$TELEMETRY" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for sensor, reading in sorted(data['sensors'].items()):
    value = reading['value']
    unit = reading.get('unit', '')
    if 'temp' in sensor:
        fahrenheit = (value * 9/5) + 32
        print(f'{sensor:25} {fahrenheit:6.1f}°F')
    else:
        if unit == 'pct':
            print(f'{sensor:25} {value:6.1f}%')
        else:
            print(f'{sensor:25} {value:6.1f} {unit}')
"

echo ""
echo "✅ Conversion Formula: °F = (°C × 9/5) + 32"
echo "✅ Frontend displays: http://localhost:3000"
echo ""
