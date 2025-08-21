# Development Guide

This document provides guidance for developers working on the Cowrie IRC Bot project.

## Setting up Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/cowrie-irc-bot.git
   cd cowrie-irc-bot
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   pip install -e ".[dev,geo]"
   ```

## Development Workflow

### Running the Bot

For development, you can run the bot directly:

```bash
# Using the default config
python -m src.main

# Using a custom config
python -m src.main --config path/to/config.json

# With custom log file
python -m src.main --log-file path/to/cowrie.log
```

### Testing

Run all tests:

```bash
python -m unittest discover tests
```

Run specific test:

```bash
python -m unittest tests.test_parser
```

Run tests with coverage:

```bash
pytest --cov=src tests/
```

### Adding New Features

1. Create a new branch for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Implement your feature, following the existing code structure and style.

3. Add tests for your new feature in the `tests/` directory.

4. Run the tests to ensure everything passes:
   ```bash
   python -m unittest discover tests
   ```

5. Submit a pull request.

## Project Structure

- `src/`: Source code
  - `log_monitor/`: Modules for Cowrie log monitoring and parsing
  - `irc_client/`: IRC client and message formatting
  - `stats/`: Statistics collection and reporting
  - `utils/`: Utilities including configuration and geolocation
  - `main.py`: Application entry point

- `tests/`: Test modules
- `scripts/`: Installation and utility scripts
- `docs/`: Documentation

## Adding New Event Types

To add support for a new Cowrie event type:

1. Update the `CowrieLogParser` in `src/log_monitor/parser.py`:
   - Add pattern recognition for the new event
   - Implement parsing logic in `parse_entry()` method
   - Add logic in `_determine_event_type()` method

2. Add message formatting in `IRCFormatter` in `src/irc_client/formatter.py`:
   - Create a new formatting method for your event type
   - Include both colored and non-colored versions

3. Update the `_handle_log_line()` method in `src/main.py` to handle the new event type

4. Add tests for the new event type in `tests/test_parser.py`

## Debugging

Enable debug logging by running the bot with:

```bash
python -m src.main --log-level DEBUG
```

You can also save logs to a file:

```bash
python -m src.main --log-file-path ./debug.log --log-level DEBUG
```