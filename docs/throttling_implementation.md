# Throttling Implementation Documentation

## Overview

This document describes the thread throttling and startup staggering implementation for the YouTube automation system. The implementation ensures efficient resource usage and prevents system overload by controlling concurrent instances and spacing out Chrome browser launches.

## Key Features

### 1. Semaphore-Based Concurrency Control

- **Implementation**: Uses Python's `threading.Semaphore` to limit concurrent instances
- **Configuration**: `max_concurrent_instances` in `config.json` (default: 5)
- **Location**: `src/main_controller.py`

```python
# Semaphore creation in __init__
self.instance_semaphore = threading.Semaphore(max_concurrent)

# Usage in start_automation
self.instance_semaphore.acquire()  # Wait for available slot
# ... start instance ...
# Semaphore is released in _run_account_instance_with_semaphore
```

### 2. Staggered Instance Startup

- **Purpose**: Prevents simultaneous Chrome spawning which causes port conflicts and CPU spikes
- **Configuration**: `instance_startup_delay` in `config.json` (default: 10 seconds)
- **Implementation**: `time.sleep(startup_delay)` between instance launches

### 3. Thread Lifecycle Management

Each instance follows this lifecycle:

1. **Acquire Semaphore**: Wait for available slot
2. **Start Thread**: Launch instance in separate thread
3. **Create Browser**: Initialize Chrome driver
4. **Login**: Authenticate with Gmail
5. **Run Automation**: Execute YouTube loops
6. **Cleanup**: Close browser and release semaphore

### 4. Auto-Restart with Throttling

- Crashed instances can be automatically restarted
- Restart attempts also respect the semaphore limit
- Uses `acquire(blocking=False)` to avoid blocking the monitoring thread

## Configuration

In `config.json`:

```json
{
  "automation_settings": {
    "max_concurrent_instances": 5,      // Maximum concurrent Chrome instances
    "instance_startup_delay": 10,       // Seconds between instance launches
    "monitoring_interval": 30,          // Seconds between monitoring checks
    "auto_restart_on_crash": true       // Enable automatic restart of crashed instances
  }
}
```

## Benefits

1. **Resource Management**: Prevents system overload by limiting concurrent Chrome instances
2. **Stability**: Reduces crashes caused by resource exhaustion
3. **Port Management**: Staggered startups prevent port conflicts
4. **CPU Optimization**: Spreads CPU load over time instead of creating spikes
5. **Memory Control**: Limits total memory usage by controlling instance count

## Monitoring

The system provides detailed logging for throttling behavior:

- Instance slot acquisition and release
- Wait times for slots
- Active instance counts
- Thread lifecycle events

## Testing

Use `test_throttling.py` to verify the implementation:

```bash
python test_throttling.py
```

This test script:
- Displays current configuration
- Shows expected behavior
- Monitors resource usage
- Provides detailed logging of throttling actions

## Example Output

```
[Main Controller] Instance 1/7 - Active: 0/5
[Main Controller] Slot available for Account1
[Main Controller] Started instance for Account1 (Thread ID: 12345)
[Main Controller] Staggering startup: waiting 10s before next instance...

[Main Controller] Instance 6/7 - Active: 5/5
[Main Controller] Max instances reached. Waiting for slot (account: Account6)...
[Main Controller] Acquired slot after 15.2s wait
[Main Controller] Thread started for Account6
```

## Troubleshooting

1. **Instances not starting**: Check if semaphore value is > 0 in config
2. **All slots occupied**: Increase `max_concurrent_instances` if system can handle it
3. **High CPU on startup**: Increase `instance_startup_delay`
4. **Memory issues**: Decrease `max_concurrent_instances`

## Future Enhancements

1. Dynamic throttling based on system resources
2. Priority queue for account scheduling
3. Adaptive startup delays based on system load
4. Per-account instance limits
