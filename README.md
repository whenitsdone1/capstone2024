Flask utility using a PocketBase backend for managing submissions of quality assurance forms for the La Trobe Computer Science and Information Technology Department.


# Running the application

`python app.py`

# PocketBase

Upon first downloading and starting PocketBase, you will need to make a admin account - you will use some of those details in your `secrets.env` file. Other than that, all databases and related operations are handled with through the application.

You must launch PocketBase *independently* of the Flask application the first time in order to make your admin acccount.

You can do this with:

`./pocketbase serve` in the project root.

PocketBase should then be automatically started and ended with the Flask application - see `handle_PB.py` for implementation.
However, if you neeed to start PocketBase yourself after this, you can do so with:

`./pocketbase serve --dir <your_directory>` 

Where your directory is the directory you are storing your database `pb_data`

For example, on the development setup:

`./pocketbase serve --dir ./pb_data`

If you need to end the PocketBase process yourself, you can get the PID from the log files.

`kill PID`

# secrets.env

You will need a secrets.env file (one within the tests directory AND one within the parent directory), with the following entries:

`POCKETBASE_URL="THE URL OF YOUR POCKETBASE INSTANCE"`

`POCKETBASE_ADMIN_EMAIL="YOUR ADMIN EMAIL"`

`POCKETBASE_ADMIN_PASSWORD=YOUR ADMIN PASSWORD`

`FLASK_ENV="THIS SHOULD LIKELY BE 'production' IF YOU DON'T KNOW WHAT THIS IS"`

`GOOGLE_API_KEY="YOUR GEMINI API KEY"`

`TEST_EMAIL="THE ADDRESS YOU WANT TEST EMAILS SENT TO"`


# Gmail API

You will need to get access to the gmail API here:

https://developers.google.com/gmail/api/guides

Follow the instructions - you will need to download a `client_secret.json` file to the project directory in order to use the gmail API. 

Authentication for the gmail API happens in the console when you run `mail.py` with a `client_secret.json` file in the project directory, as I wrote this in a headless environment (WSL)

# Gemini

To use the Gemini LLM API you will need to get an API key from here:

https://ai.google.dev/

# Dependencies 

To install the projects required modules:


`python install_dependencies.py`

