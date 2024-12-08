# Eco-cheep

Eco-cheep is a gamified sustainability platform designed to encourage eco-friendly practices. Users complete sustainability tasks, interact with their virtual pet Cheep, and receive actionable suggestions to improve their impact on the environment.

You can try it at: https://eco-cheep.onrender.com/

## Features

- **User Authentication:** Secure login and signup system.
- **Cheep Interaction:** Engage with your virtual pet and build a relationship by completing quests.
- **Quest Management:** Add, view, and complete sustainability tasks to level up your eco-friendliness.
- **Image Verification:** Upload images as proof of task completion, verified using AI.
- **Personalized Suggestions:** Receive context-based recommendations to enhance your sustainability journey.

## Installation

To install and run the Eco-cheep application locally, follow these steps:

1. Clone the repository:
    ```bash
    git clone https://github.com/aqts-aqts/Eco-cheep.git
    ```
2. Navigate to the project directory:
    ```bash
    cd eco-cheep
    ```
3. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4. Create a .env with your OpenAI key and MongoDB URI:
    ```bash
    OPENAI_KEY=YOUR_OPENAI_KEY
    MONGO_URI=DB_URI
    ```
5. Create a database "ecocheep", and a collection "users" inside Mongo.

## Usage

Once the application is running, you can access it at `http://localhost:5000`.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
