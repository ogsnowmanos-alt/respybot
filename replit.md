# Discord Bot Dashboard

## Overview

This project is a Discord bot with an integrated Flask web dashboard for monitoring and management. The application runs both a Discord bot and a web server concurrently, allowing users to view bot status, health metrics, and operational details through a web interface. The bot uses Discord.py for bot functionality and Flask for the web dashboard, with a dark-themed Bootstrap UI for a modern user experience.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Concurrent Service Architecture
The application uses a dual-service architecture where both Flask web server and Discord bot run simultaneously in separate threads. The main.py file orchestrates this by starting Flask in a daemon thread and running the Discord bot in the main thread, ensuring both services remain operational.

### Web Dashboard Framework
Flask serves as the web framework with Jinja2 templating for dynamic content rendering. The application uses Bootstrap with a dark theme for consistent UI styling and Font Awesome for iconography. ProxyFix middleware handles proxy headers for proper deployment behind reverse proxies.

### Bot Framework
Discord.py provides the core bot functionality with configurable intents for message content and guild access. The bot implements event handlers for connection lifecycle management and includes slash command synchronization for modern Discord interactions.

### Status Monitoring System
A global bot status tracking system maintains real-time information about bot connectivity, guild count, latency, and user details. This status is exposed through both web pages and REST API endpoints for programmatic access.

### Routing and API Structure
The application separates concerns with dedicated route handlers in routes.py, providing both HTML pages for human interaction and JSON API endpoints for programmatic access. Health check endpoints enable monitoring and alerting capabilities.

### Template Architecture
HTML templates use Bootstrap's dark theme with responsive design patterns. The navigation structure provides easy access to different views including home dashboard, detailed status pages, and health monitoring endpoints.

### Error Handling Strategy
Comprehensive logging throughout the application captures errors at different layers. Error boundaries in route handlers ensure graceful degradation when services encounter issues, with user-friendly error messages displayed in the web interface.

## External Dependencies

### Discord Integration
- **discord.py**: Core Discord bot library for API communication, event handling, and slash command management
- **Discord Developer Portal**: Bot token and application configuration

### Web Framework
- **Flask**: Lightweight web framework for dashboard and API endpoints
- **Werkzeug**: WSGI utilities including ProxyFix middleware for deployment

### Frontend Libraries
- **Bootstrap**: CSS framework with dark theme from cdn.replit.com
- **Font Awesome**: Icon library for UI enhancement
- **Jinja2**: Template engine for dynamic HTML generation

### Development and Deployment
- **Python standard library**: Threading, logging, asyncio for concurrent operations
- **Environment variables**: Configuration management for secrets and deployment settings