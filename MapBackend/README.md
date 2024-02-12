
# Map Making Game

## Project Overview
Map Making Game is a scripting class project focused on creating an interactive game environment where players can join teams, navigate a map, and place or remove objects. The game is built in phases, starting with basic map and player interactions, eventually moving towards a more complex system with user authentication and advanced game features.

```
MapMakingGame/
│
├── assets/                  # Directory for static files like images and maps.
│   ├── maps/
│   └── images/
│
├── src/                     # Source files for the game scripts.
│   ├── main.py              # Main script to run the game.
│   ├── map.py               # Script containing the Map class.
│   ├── player.py            # Script containing the Player class.
│   ├── objects.p            # Script for different game object classes.
│   └── utils/               # Utility scripts, like for handling configurations.
│       └── config.py        # Script for managing game configurations.
│
├── tests/                   # Unit tests for your game classes and functions.
│   └── test_map.py          # Tests for the Map class.
│
└── README.md                # Documentation for setting up and playing the game.
```

## Setup
To set up the Map Making Game, follow these steps:

1. Clone the project repository to your local machine.
   ```sh
   git clone [repository_url]
   ```
2. Navigate to the project directory.
   ```sh
   cd MapMakingGame
   ```
3. Install the required dependencies (if any).
   ```sh
   pip install -r requirements.txt
   ```
4. Run the `main.py` script to start the game.
   ```sh
   python src/main.py
   ```

## Project Structure
- `assets/`: Contains static files like images and map layouts.
- `src/`: Contains the source code for the game.
- `tests/`: Contains unit tests for the game components.
- `README.md`: This file, which includes setup instructions and project information.

## Next Steps
### Phase 1: Basic Map and Player Setup
- Implement the `Map` class with methods to add and remove objects.
- Create the `Player` class with movement and object interaction capabilities.

### Phase 2: Advanced Map Features
- Develop advanced map features like different terrains and obstacles.
- Implement the team view of the map with fog of war concept.

### Phase 3: User Interaction
- Create a user interface for players to interact with the game.
- Develop a system for players to join and leave the game dynamically.

### Phase 4: Game Persistence and Threading
- Add database support to save game states and player progress.
- Introduce threading for handling multiple player actions simultaneously.

### Testing and Documentation
- Write unit tests for each new feature added.
- Ensure that all methods and classes are well-documented.

### Deployment
- Prepare the game for deployment, ensuring all assets are correctly bundled.
- Test the game in a production-like environment.

## Contribution
Please read `CONTRIBUTING.md` for details on our code of conduct, and the process for submitting pull requests to us.

## License
This project is licensed under the MIT License - see the `LICENSE.md` file for details.

## Acknowledgments
- Thanks to the scripting class instructor and TAs.
- Shoutout to all the team members who have contributed to this project.