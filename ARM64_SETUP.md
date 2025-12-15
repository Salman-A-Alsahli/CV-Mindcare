# ARM64 / Raspberry Pi Setup Guide

## Quick Fix for Rollup Module Error

If you see this error on Raspberry Pi or any ARM64 system:

```
Error: Cannot find module @rollup/rollup-linux-arm64-gnu
npm has a bug related to optional dependencies
```

**Quick Solution:**

```bash
# From the CV-Mindcare root directory
./setup-frontend.sh
```

This script automatically detects ARM64 architecture and applies the necessary workarounds.

---

## What Changed

We've added ARM64-specific support to CV-Mindcare:

### 1. Enhanced Setup Script (`setup-frontend.sh`)
- Automatically detects ARM64 architecture
- Cleans previous installations that may have failed
- Uses `--legacy-peer-deps --force` flags for npm install
- Explicitly installs Rollup ARM64 module if missing

### 2. Smart Start Script (`start-dashboard.sh`)
- Checks for ARM64 architecture
- Verifies Rollup module is present before starting
- Provides helpful error messages with fix instructions
- Better error handling and cleanup

### 3. NPM Configuration (`.npmrc`)
- Optimized for ARM64 platforms
- Handles optional dependencies correctly
- Increased timeouts for slower ARM platforms
- Better retry logic

### 4. Comprehensive Documentation
- Added detailed troubleshooting in `docs/TROUBLESHOOTING.md`
- Updated Raspberry Pi guide with ARM64 instructions
- Added prevention tips and references

---

## Why This Happens

The issue occurs because:

1. **Rollup requires platform-specific native modules** - Different binaries for x64, ARM64, etc.
2. **npm has a known bug** with optional dependencies on ARM64 ([npm#4828](https://github.com/npm/cli/issues/4828))
3. **Standard `npm install` may skip** the `@rollup/rollup-linux-arm64-gnu` package

---

## Prevention

To avoid this issue in the future:

1. **Always use the setup script** for initial installation
2. **Keep Node.js updated** to version 18 or higher
3. **Keep npm updated** to the latest version
4. **Use the start script** which includes ARM64 checks

---

## Manual Fix (if script doesn't work)

```bash
cd frontend

# Clean everything
rm -rf node_modules package-lock.json

# Reinstall with ARM64-friendly flags
npm install --legacy-peer-deps --force

# If still missing, install explicitly
npm install @rollup/rollup-linux-arm64-gnu --save-optional --force

# Verify
ls -la node_modules/@rollup/rollup-linux-arm64-gnu/
```

---

## System Requirements

- **Node.js:** 18.0.0 or higher
- **npm:** 9.0.0 or higher
- **Architecture:** ARM64 / aarch64 (Raspberry Pi 4/5)
- **OS:** Raspberry Pi OS (64-bit) or compatible Linux

---

## Related Resources

- [Full Troubleshooting Guide](docs/TROUBLESHOOTING.md#9-rollup-module-error-on-arm64-raspberry-pi)
- [Raspberry Pi Deployment Guide](docs/deployment/raspberry-pi.md)
- [npm issue #4828](https://github.com/npm/cli/issues/4828)
- [Vite/Rollup ARM64 compatibility](https://github.com/vitejs/vite/issues/6315)

---

## Testing

After applying the fix:

```bash
# Test backend
cd ~/CV-Mindcare
source .venv/bin/activate
python -c "from backend.app import app; print('✅ Backend OK')"

# Test frontend
cd ~/CV-Mindcare/frontend
npm run dev

# Or use the combined launcher
cd ~/CV-Mindcare
./start-dashboard.sh
```

Expected output: Dashboard should start without errors at http://localhost:5173

---

## Support

If you still have issues after trying these solutions:

1. Check the [Troubleshooting Guide](docs/TROUBLESHOOTING.md)
2. Review [GitHub Issues](https://github.com/Salman-A-Alsahli/CV-Mindcare/issues)
3. Create a new issue with:
   - Your architecture (`uname -m`)
   - Node.js version (`node --version`)
   - npm version (`npm --version`)
   - Full error message
   - Output of `./setup-frontend.sh`

---

**Last Updated:** December 2024  
**Applies to:** CV-Mindcare v1.0.0+  
**Platforms:** ARM64, Raspberry Pi 4/5
