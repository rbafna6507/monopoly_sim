# Monopoly Simulation

This repository contains two main parts: a Flask API and a React frontend.

This is a simulation of Monopoly using a Monte Carlo approach to determine the optimal strategy for buying properties.

## Introduction

This Monopoly simulation models Monopoly using a Monte Carlo (predicted future value using hueristics) approach to determine the optimal strategy for buying properties. The simulation utilizes websockets to allow real time updates to the simulation's React-based frontend.

Broadly, this simulation focuses on the core rules of Monopoly: deciding when to buy and sell properties to optimize for cash and becoming a monopoly. The game terminates when all players except one have gone bankrupt.

Key features of the simulation include:
- Cash reserve management
- Property aquisition
- Risk-adjusted purchasing decisions
- Real-time updates to the frontend

The Flask backend handles all game logic and statistical calculations, while the React frontend provides a chart-based and monopoly board visualization of the simulation. It also details the simulation's decision making engine and why specific actions were taken.

The backend contains two main components: `monopoly_sim`, which contains the logic for running the simulation, and `sim_socket`, which contains the websocket logic for the frontend to interface with the simulation. The React frontend lives in the `/monopoly_simulation` directory.


### Getting Started

To start, make sure you have python version 3.9.7 (or newer) and the latest version of this repository cloned locally. 

Next, cd into the `/monopoly` directory, where the Flask server's code lives:

Once in the directory, execute the following command to create a python virtual environment:

`python -m venv venv`

Once the virtual environment is created, run the following commands while in the solution directory to activate the virtual environment, and install the necessary packages to run the API.
```
. venv/bin/activate
pip install -r requirements.txt

```
Now that all the necessary packages are installed, you're ready to run the API locally.

To start the API on a local development server on http://127.0.0.1:5000 (port 5000) run:

`python api/sim_socket.py`


Next you'll want to start the React app to interface with the API.

To start, jump into the `/monopoly-simulation` folder, where the React code lives. Here you'll want to install all the related npm packages using:

`npm install`

And to finally run the react app on http://127.0.0.1:3000 (port 3000), you can run:

`npm start`

You now have a fully set up environment, and will be able to use both the Flask API and the React frontend.

### Take Aways + Next Steps

Because of the time contraints of this problem, a few tradeoffs were made:

1) Simulation Functionality

I decided to forgo some of the key monopoly rules to keep the simulation simple. For example, I did not implement the following:
- Houses
- Hotels
- Mortagaging
- Community Chest and Chance card spaces

Given more time, I would have liked to implement these features, particularly house building and mortaging as they offer another layer of complexity and strategy to the simution.


2) Strategy

While the strategy I implemented has complexity and determines whether a property is a 'good buy' based on a number of critera, there is still room to make it more robust and accurate. Potential improvements include: fully cloning game state and running 40 turns into the future to determine a more realistic 'property value'.

3) Frontend

The frontend serves as a visualiation tool for the meat behind the project. Given more time, I'd like to polish it off, make it more interactive, and add some more charts and statistics. In particular, modifying the websocket logic to allow for multiple concurrent connections is something that is non-negotiable for a polished application.



Thanks for reading.

&ndash; Rohan