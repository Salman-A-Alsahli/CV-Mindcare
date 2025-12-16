# Simulation Toggle Bug Fix

## Problem
Users reported that when they turned on the simulation, it would automatically turn back off on its own.

## Root Cause
The bug was caused by a **deadlock** in the `start_simulation()` method in `sensor_manager.py`. Here's what was happening:

1. When `start_simulation()` was called, it acquired a lock using `with self._lock:`
2. Inside the locked section, if real sensors were running, it called `self.stop_all()`
3. The `stop_all()` method also tried to acquire the same lock with `with self._lock:`
4. Since Python's `threading.Lock()` is **not reentrant**, attempting to acquire it twice from the same thread causes a deadlock

The code flow looked like this:
```python
def start_simulation(self, scenario: str = "calm") -> bool:
    with self._lock:  # ← Lock acquired here
        if self.running and not self.simulation_mode:
            self.stop_all()  # ← Tries to acquire lock again! DEADLOCK!
```

## Solution
Changed `threading.Lock()` to `threading.RLock()` (reentrant lock) in the `SensorManager.__init__()` method:

```python
# Before:
self._lock = threading.Lock()

# After:
self._lock = threading.RLock()  # Use reentrant lock to prevent deadlock
```

A reentrant lock allows the same thread to acquire the lock multiple times, preventing the deadlock.

## Changes Made
- **File**: `backend/sensors/sensor_manager.py`
- **Line**: 103
- **Change**: `threading.Lock()` → `threading.RLock()`

## Testing
1. **Unit Tests**: All 16 simulation controller unit tests passed
2. **Integration Tests**: All 10 simulation API integration tests passed
3. **Manual Test**: Created and ran a persistence test that:
   - Started the simulation
   - Monitored status every 3 seconds for 15 seconds
   - Verified simulation stayed active throughout
   - Successfully stopped the simulation

## Impact
- **Minimal change**: Only one line changed (lock type)
- **No breaking changes**: All existing tests pass
- **Performance**: RLock has negligible performance overhead compared to Lock
- **Thread safety**: Maintains all thread safety guarantees

## Verification
To verify the fix works:

1. Start the backend server:
   ```bash
   cd /home/runner/work/CV-Mindcare/CV-Mindcare
   python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
   ```

2. In the frontend, toggle the simulation on
3. The simulation should stay on and not turn off automatically
4. The status should remain `active: true` when refetched every 3 seconds

## Additional Notes
This is a classic threading bug pattern where non-reentrant locks cause deadlocks when methods call other methods that also need the same lock. Using `RLock` is the standard Python solution for this scenario.
