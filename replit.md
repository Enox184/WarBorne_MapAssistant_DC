# Discord Regeneration Timer Bot

## Overview

This is a Discord bot designed to track regeneration timers for game content across different maps. The bot allows users to set timers for various types of resources (like scrap posts, orbs, chests, and materials) and tracks when they will regenerate. It's specifically tailored for a gaming community that needs to coordinate resource collection timing.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Bot Framework
- **Discord.py Library**: Uses the modern discord.py library with slash commands (app_commands) for a better user experience
- **Command System**: Implements both traditional prefix commands (!) and modern slash commands for flexibility
- **Event-Driven Architecture**: Built on Discord's event-driven model with proper intent handling

### Data Management
- **JSON File Storage**: Uses simple JSON file persistence (`map_data.json`) for storing timer data
- **In-Memory Cache**: Maintains `client.map_times` dictionary for fast access to timer data
- **Data Persistence**: Implements load/save functions that handle file operations and error cases gracefully

### Timer System
- **UTC Timezone Handling**: Uses UTC timestamps for consistent time tracking across different user timezones
- **Resource Type Validation**: Predefined list of valid resource types (`SUROWCE`) to ensure data consistency
- **Time Formatting**: Custom time formatting function for user-friendly display of countdowns

### Command Structure
- **Slash Command Integration**: Modern Discord slash command implementation with parameter descriptions
- **Type Safety**: Uses app_commands.describe for parameter validation and user guidance
- **Modular Design**: Helper functions separated for reusability and maintainability

### Resource Management
The bot tracks 13 different resource types:
- Scrap posts (small, medium, big)
- Orbs (green, blue, purple, gold)
- Chests (green, blue, purple, gold)
- Materials (scrap iron, resin)

## External Dependencies

### Core Dependencies
- **Discord.py**: Modern Discord API wrapper for bot functionality
- **Python Standard Library**: 
  - `datetime` for timestamp and timer calculations
  - `json` for data serialization
  - `os` for environment variable access

### Environment Configuration
- **DISCORD_TOKEN**: Bot authentication token stored as environment variable for security

### Data Storage
- **Local JSON File**: `map_data.json` serves as the persistent storage solution
- **File System**: Relies on local file system for data persistence (suitable for single-instance deployment)

Note: The current architecture uses local file storage which works well for small-scale deployments but may need to be upgraded to a database solution for larger scale or multi-instance deployments.