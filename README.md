
# Project Documentation - Dev Backend Case

## The following was requested:

- Develop a small system and an HTTP API for a knockout tournament.
- In each round, competitors are randomly paired and compete against each other.
- The winners move on to the next round, competing against other winners until only two competitors remain.
- The last two competitors determine the winner and the second place in the final round.
- The losers of the penultimate round compete among themselves to determine the third and fourth places.
- If it is not possible to pair all competitors in the first round, some automatically move to the second round.

## How to Run with Docker

To run this project in a Docker container, eliminating the need to install dependencies locally, follow these steps:

### Container Construction

First, ensure that Docker is installed on your system.

1. Clone this repository to your computer.
2. Run the Docker build command to create the container image:

```bash
docker build -t image-name .

```

### Container Execution

1. Now, you can run the Docker container created with the following command:

```bash
docker-compose up -d

```

### To run tests inside the container:

1. In your terminal, simply run this command in the same directory where the docker compose is located

```bash
docker-compose run --entrypoint="poetry run task test" {nome do app}
```


## Use Taskipy

This project uses Taskipy to simplify common development tasks, such as code formatting and checking. Following are the commands available in Taskipy:

To execute the commands, open a terminal in the root directory of the project and run the following command:

```bash
task format
```

- This command will apply formatting to the Python code in the current directory and subdirectories, following the pep8 conventions. It is a good practice to run this command before submitting your code for review or when you wish to maintain consistent formatting.

```bash
task run

```

This command will start the execution of the project, which should be configured in the **app**.py file.

To view the test **coverage** of the project

```bash
task post_test
```

Format the code using blue and isort

```bash
task format

```

Runs ruff to check if we have any problems with the code and checks if we are in accordance with PEP-8

```bash
task lint
```

## CI teste

This project utilizes Continuous Integration (CI) within the repository. Any code committed to the repository must adhere to PEP-8 standards and maintain a minimum test coverage of 90% to pass.



## Project architecture
```

|─ app
│   ├── app.py
│   ├── database.py
│   ├── __init__.py
│   ├── migrations
│   │   ├── __pycache__
│   │   └── versions
│   ├── models.py
│   ├── routes
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── schemas.py
│   ├── settings.py
│   └── tests
├── docker-compose.yaml
├── dockerfile
├── entrypoint.sh
├── htmlcov
│   ├── coverage_html.js
│   ├── index.html
├── migrations
├── poetry.lock
├── pyproject.toml
├── README.md
├── tests
│   ├── conftest.py
│   ├── __init__.py
│   │   ├── conftest.pyc
│   │   ├── __init__.cpython-311.pyc
│   │   ├── test_db.pyc
│   │   └── test_routes.pyc
│   ├── test_db.py
│   └── test_routes.py
```

## Technologies Used:

- Fastapi
- SQLAlchemy
- Docker
- Pydantic
- Taskipy
- Alembic
- iSort
- Ruff
- CI for test


## **Create Tournament**

### **Request**

- **Endpoint:** **`/tournament`**
- **Method:** **`POST`**
- **Description:** Create a new tournament.
- **Rules**: 
    - No two championships can share the same name and dates.

    - The end date of a championship cannot precede its start date.

### Example

```json
jsonCopy code
{
  "name": "Example Tournament",
  "date_start": "2024-01-29T12:00:00",
  "date_end": "2024-02-05T18:00:00"
}

```

### **Response**

- **Status Code:** **`201 Created`**
- **Response Body:**

```json
jsonCopy code
{
  "id": "tournament_id",
  "name": "Example Tournament",
  "date_start": "2024-01-29T12:00:00",
  "date_end": "2024-02-05T18:00:00"
}

```

## **Register Competitors**

### **Request**

- **Endpoint:** **`/tournament/{tournament_id}/competitor`**
- **Method:** **`POST`**
- **Description:** Register competitors for a tournament.
- **Rules:** 

    - Competitors can only be registered for a championship once; the championship begins immediately after this.

   -  A minimum of two competitors is allowed for registration.

### Example

```json
jsonCopy code
{
  "names": ["Competitor1", "Competitor2"]
}

```

### **Response**

- **Status Code:** **`201 Created`**

## **Get Match List**

### **Request**

- **Endpoint:** **`/tournament/{tournament_id}/match`**
- **Method:** **`GET`**
- **Description:** Retrieve the list of matches for a tournament.
- **Rules:** - 

  - **Running the Route:** This action generates and lists matches.
  - **Pending Matches:** If there are pending matches, new matches for the next round will not be created.
  - **Three-Person Championship:** In the case of a three-person championship, running the route will generate a placeholder match, guaranteeing a third place. A separate request is required to generate the final match where the winner can be declared.

### **Response**

- **Status Code:** **`201 Created`**
- **Response Body:**

```json
jsonCopy code
{
  "Round 1": [
    {
      "id": "match_id",
      "competitor_1": "Competitor1",
      "competitor_2": "Competitor2",
      "state": "pending",
      "id": 1,
      "round": 2
    }
  ]
}

```

## **Set Winner for a Match**

### **Request**

- **Endpoint:** **`/tournament/{tournament_id}/match/{match_id}`**
- **Method:** **`POST`**
- **Description:** Set the winner for a match.
- **Rules:**

  - Only one winner can be added at a time per round.
  - The name must match their name in the tournament, including the last distinguishing characters.

### Example

```json
jsonCopy code
{
  "name": "Competitor1"
}

```

### **Response**

- **Status Code:** **`201 Created`**

## **Get Tournament Results**

### **Request**

- **Endpoint:** **`/tournament/{tournament_id}/result`**
- **Method:** **`GET`**
- **Description:** Retrieve the results of a tournament.

### **Response**
```json
jsonCopy code
{
  [
    "First": "competitor 1",
    "Second": "competitor 2 -10",
  ]
}

```


- **Status Code:** **`201 Created`**


## Class Documentation




### Tournament Class

The Tournament class represents a sports tournament in the database. It is designed to store information about different tournaments, including their name, start and end dates, participating competitors, number of matches, and active status.

### Attributes

- `id` (int): Unique identifier for the tournament (Primary Key).
- `name` (str): Name of the tournament.
- `date_start` (datetime): Start date and time of the tournament.
- `date_end` (datetime): End date and time of the tournament.
- `competitors` (relationship): Relationship with the 'Competitor' class.
- `number_matches` (int, optional): Number of matches in the tournament (can be None).
- `is_active` (bool): Indicates whether the tournament is active or not.

### Methods

- `create_tournament(session, **kwargs) -> Tournament`
    
    Creates a new tournament.
    
    ### Parameters:
    
    - `session` (Session): SQLAlchemy session.
    - `*kwargs`: Additional tournament data.
    
    ### Returns:
    
    - `Tournament`: The created tournament.
    
    ### Raises:
    
    - `ValueError`: If an error occurs during tournament creation.

### Competitor Class

The Competitor class represents participants in a sports tournament. It is designed to store information about competitors, including their name, group, associated tournament, and status.

### Attributes

- `id (int)`: Unique identifier for the competitor (Primary Key).
- `name (str)`: Name of the competitor.
- `group (Enum)`: Competitor's group (e.g., 'group_1' or 'group_2').
- `tournament_id (int)`: Foreign key referencing the associated tournament.
- `tournament (relationship)`: Relationship with the 'Tournament' class.
- `status (bool)`: Indicates the competitor's active status.

### Methods

### _number_of_matches(number_competitors) -> int

This function calculates the number of matches needed for a tournament based on the number of competitors.

**Parameters:**

- `number_competitors (int)`: Number of competitors in the tournament.

**Returns:**

- `int`: Number of matches.

### create_competitors(names, tournament_id, session) -> None

Creates competitors, validates the associated tournament, and adds competitors to groups based on the tournament's brackets.

**Parameters:**

- `names (list)`: List of competitor names.
- `tournament_id (int)`: ID of the associated tournament.
- `session (Session)`: SQLAlchemy session.

**Raises:**

- `ValueError`: If the tournament ID is not found, the tournament has already started, or there are fewer than 2 competitors.


### Match Class

The `Match` class represents individual matches within a sports tournament. It manages the pairing of competitors, tracks the winner, and maintains the state of each match.

### Attributes

- **id (int):** Unique identifier for the match (Primary Key).
- **competitor_1_id (int):** Foreign key referencing the first competitor.
- **competitor_2_id (int):** Foreign key referencing the second competitor.
- **winner_id (int):** Foreign key referencing the winner.
- **tournament_id (int):** Foreign key referencing the associated tournament.
- **competitor_1 (relationship):** Relationship with the 'Competitor' class for the first competitor.
- **competitor_2 (relationship):** Relationship with the 'Competitor' class for the second competitor.
- **winner (relationship):** Relationship with the 'Competitor' class for the winner.
- **tournament (relationship):** Relationship with the 'Tournament' class.
- **round (int):** Round number of the match.
- **state (Enum):** State of the match ('pending' or 'finished').

### Methods

#### `_set_pair(names) -> list[tuple[Competitor]]`

Sets pairs for the matches based on the provided list of competitor names. If the list has an odd length, one competitor is placed alone in a tuple.

#### Parameters:

- `names (list):` List of competitor names.

#### Returns:

- `list[tuple[Competitor]]:` Pairs of competitors for the matches.

#### `create_match(tournament_id: int, session: Session) -> None`

Creates matches for a tournament, verifies if it is the last round, and adds competitors to their respective matches.

#### Parameters:

- `tournament_id (int):` ID of the associated tournament.
- `session (Session):` SQLAlchemy session.

#### `list_matches(tournament_id: int, session: Session) -> dict`

Lists all matches from a tournament in a dictionary format.

#### Parameters:

- `tournament_id (int):` ID of the associated tournament.
- `session (Session):` SQLAlchemy session.

#### Returns:

- `dict:` Dictionary with rounds and match details.


#### `set_winner`

Sets the winner of a match and updates the state of the competitors.

### Parameters

- `match_id (int):` Unique identifier for the match.
- `name (str):` Name of the winner.
- `session (Session):` SQLAlchemy session.

### Returns

- `Match:` The updated match.

#### `get_topfour`

Fetches the finalists, determines the winner, 2nd place, fetches the semifinalists, and determines the 3rd and 4th places.

### Parameters

- `tournament (int):` ID of the associated tournament.
- `session (Session):` SQLAlchemy session.

### Returns

- `dict:` Dictionary with information about the top four competitors.

#### `_create_consolation_match`

Creates a consolation match for a tournament.

### Parameters

- `tournament_id (int):` ID of the tournament.
- `last_round (int):` The last round number.
- `session (Session):` SQLAlchemy session.

#### `_should_create_consolation`

Verifies if a consolation match should be created.

### Parameters

- `total (int):` Total number of matches expected.
- `matches (list[Match]):` List of matches.

### Returns

- `bool:` True if a consolation match should be created, False otherwise.
