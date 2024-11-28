## Monopoly Simulation

This repository contains two main parts: a Flask API and a React frontend.

This is a simulation of Monopoly using a Monte Carlo approach to determine the optimal strategy for buying properties.

# Introduction


# Getting Started

To start, make sure you have python version 3.9.7 (or newer) and the latest version of this repository cloned locally. 

Next, cd into the `/monopoly` directory, where the Flask server's code lives:

Once in the directory, execute the following command to create a python virtual environment:

`python -m venv venv`

Once the virtual environment is created, run the following commands while in the solution directory to activate the virtual environment, and install the necessary packages to run the API.
```
. venv/bin/activate
pip install -r requirements.txt
Now that all the necessary packages are installed, you're ready to run the API locally.
```

To start the API on a local development server on http://127.0.0.1:5000 (port 5000) run:

`python api/mp_api.py`


Next you'll want to start the React app to interface with the API.

To start, jump into the `/monopoly-simulation` folder, where the React code lives. Here you'll want to install all the related npm packages using:

`npm install`

And to finally run the react app on http://127.0.0.1:3000 (port 3000), you can run:

`npm start`

You now have a fully set up environment, and will be able to use both the Flask API and the React frontend.

# Capabilities

# Looking Forward

Because this was a hacky side project, there are many things that could be improved or done differently.

- The simulation could be sped up by using parallelism.

Definititely an optimization I would implement if I had more time - both because of personal interests and because it allows me to run more iterations, meaning a more accurate simulation. 

- The simulation could be made more accurate by increasing the number of iterations.
- The strategy could be improved by using a more sophisticated algorithm.
- 