# priority-queue-model

## 🎢 FastPass+ Queue Simulation 

This project simulates a two-class priority queueing system inspired by Disney's retired **FastPass+** system. Built using discrete-event simulation in Python, the model evaluates how allocating FastPasses impacts the wait times for both FastPass holders and regular guests under varying levels of theme park activity.

It was developed as part of the **Simulation & Stochastic Modeling** course at **Rollins College**.

## 📚 Background: What is FastPass+?

FastPass+ was a virtual queueing system used at Disney parks (1999-2021) that allowed guests to reserve time slots for attractions and skip the standard queue. From a simulation perspective, this create a **priority queue**, where: 

- 🎟️ **FastPass holders:** Higher priority; skip ahead of the regular line.
- 🚶🏻‍♀️ **Regular guests:** Lower priority; wait in full queue and are often preempted.

This model helps answer:
👉🏼 *What is the optimal proportion of FastPasses (`f`) to issue without degrading the experience for either group?*

## 🧠 What this simulation does

- Models a ride as an **M/M/1** system with: **exponential interarrival and service times**, two customer **classes** (FastPass and regular)
- Simulates arrivals, waiting, and service dynamics
- Varies the FastPass allocation fraction `f` from 0 to 0.95
- Tracks average residence (waiting + service) times for each group
- Repeats the analysis under: Low-load conditions where `𝜆` = 0.50, High-load conditions where `𝜆` = 0.95


## ⚙️ Requirements

- Python 3.7 or higher
- No external libraries required (uses only Python standard lobrary and `matplotlib` if plotting is enabled)


## 🚀 How to run
