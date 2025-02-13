# Project Knowledge and Conventions

## Engineering Conventions
> when plannng changes, follow these conventions.

- Activities are called by the LLM to perform tasks, return ActivityResult
- Skills are used by activities
- Framework is the core of the application, it handles the memory, state, and shared data
- Memory operations are handled in the memory.py. 
- Activities should not directly interact with the memory. Every ActivityResult should be saved to memory, and the memory module decides on further processing.

## Code Conventions
> when writing code, follow these conventions.

- Use `logger` for all logging
- Write simple, verbose code over terse, compact, dense code.
- If a function does not have a corresponding test, mention it.
- When building tests, don't mock anything.


##  Folder Structure

tests/ # the folder for the tests
my_digital_being/ # the folder for the being
├─ activities/ # Can be called by the LLM to perform tasks, return ActivityResult
├─ skills/ # used by activities
|
├─ framework/
│   ├─ main.py                     # Core DigitalBeing class, run loop
│   ├─ activity_selector.py        # Hybrid LLM + deterministic selection
│   ├─ memory.py                   # Short/long-term memory handling
│   ├─ state.py                    # Tracks energy, mood, etc.
│   ├─ shared_data.py              # Thread-safe data for cross-activity usage
│   └─ ...
├─ config/
│   ├─ character_config.json       # Where your being's name/personality go
│   ├─ activity_constraints.json   # Rate-limits, skill requirements, cooldowns
│   ├─ skills_config.json          # Enabled skills + required API keys
│   └─ ...
├─ server/
│   ├─ server.py                   # Web UI + WebSocket server
│   └─ static/                     # HTML/CSS/JS for the front-end
├─ tools/ # Dev tools
│   └─ onboard.py                  # CLI-based onboarding wizard
├─ __init__.py
├─ server.py # Web UI + WebSocket server
```
