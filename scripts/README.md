# CV-Mindcare Scripts

Utility scripts for maintenance and optimization of the CV-Mindcare system.

## Available Scripts

### Database Optimization

**optimize_database.py** - Optimize SQLite database for better performance

Applies the following optimizations:
- Enables WAL (Write-Ahead Logging) mode for better concurrency
- Optimizes synchronous mode to NORMAL for better write performance
- Increases cache size to 10MB
- Uses memory for temporary storage
- Enables auto-vacuum to reclaim space
- Analyzes tables for query optimization
- Vacuums database to reclaim space

Usage:
```bash
python scripts/optimize_database.py
```

This should be run:
- After initial setup
- Periodically (e.g., weekly) for production deployments
- After large data imports
- When experiencing performance issues

**Performance Impact:**
- Faster write operations with WAL mode
- Better concurrent access (multiple readers, one writer)
- Reduced database file size through vacuum
- Improved query performance through analysis

## Best Practices

1. **Backup before optimization**: Always backup your database before running optimization scripts
2. **Run during low usage**: Schedule optimizations during periods of low system activity
3. **Monitor results**: Check the output to ensure optimizations were applied successfully
4. **Regular maintenance**: Set up a cron job or systemd timer for regular optimization

## Future Scripts

Planned maintenance scripts:
- Data cleanup (remove old records)
- Performance benchmarking
- Health checks
- Data export/import utilities
