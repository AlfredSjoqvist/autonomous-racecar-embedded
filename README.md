# Autonomous Embedded Model Racecar

This repository contains a complete embedded and software stack for an autonomous model racecar. The system combines low level microcontroller code, real time sensor integration, LiDAR based perception, a path planning and control core on a Raspberry Pi, and a desktop user interface for manual and semi autonomous operation.

## Skills Demonstrated

- Embedded systems programming (AVR microcontrollers, C, hardware timers, interrupts)
- Real time sensor integration (gyroscope, hall sensors, LiDAR)
- Control systems and PWM based actuation (steering servo, throttle control)
- Robotics and autonomous driving concepts (mapping, localization, path planning, pure pursuit)
- Multi language software stack (Python, Rust, C, C plus vendor SDKs)
- Inter process and inter module communication (UART, TCP, USB)
- GUI development for operator interfaces and telemetry visualization
- Use of vendor SDKs (RPLIDAR) and hardware abstraction layers
- System design, modular architecture, and clean code organization
- Formal engineering documentation (requirements, design spec, test plan, time tracking)

---

## Project Structure

### `gui/`

High level user interface for interacting with the car from an external computer.

Key responsibilities:

- Manual control of throttle and steering
- Switching between manual and autonomous modes
- Display of telemetry such as speed, lap information, and planned path
- Visualization of the mapped track and the car position
- Communication with the communication module over WiFi or network sockets

Technologies:

- Python based GUI and networking
- Modular components for layout, event handling, messaging, and configuration

---

### `comm_module/`

The central coordination module running on a Raspberry Pi. This is the core of the autonomous functionality.

Key responsibilities:

- Communicating with sensor module, control module, LiDAR, and UI
- Running the mapping and localization logic
- Building and maintaining a cone based map of the track
- Planning an optimal path through the gates
- Running a pure pursuit based steering algorithm to follow the planned path
- Managing system modes (mapping phase, race phase)

Technologies:

- Python and supporting scripts
- Data structures for positions, cones, and paths
- Pathfinding, geometry, and control logic
- UART and TCP based communication

---

### `sensor/`

Firmware for the sensor module microcontroller (ATmega1284P).

Key responsibilities:

- Reading hall sensors on the rear wheels to estimate speed and distance
- Reading the gyroscope to estimate rotation
- Using hardware timers and interrupts for precise timing
- Preprocessing sensor data and streaming it to the communication module over UART

Technologies:

- C for AVR microcontrollers
- Interrupt driven design
- Fixed point style reasoning for timing and speed calculations
- JTAG and UART interfaces for debugging and communication

---

### `steering/`

Firmware for the control module that handles actuation.

Key responsibilities:

- Receiving high level speed and steering commands from the communication module
- Generating PWM signals for the throttle controller
- Generating PWM signals for the steering servo
- Ensuring smooth and stable motion based on desired inputs

Technologies:

- C for AVR microcontrollers
- Timer based PWM generation
- Simple control logic focused on reliability and responsiveness

---

### `rplidar_sdk/`

Vendor SDK and utilities for the RPLIDAR sensor used on the car.

Key responsibilities:

- Low level access to LiDAR scans
- Platform specific build files for Linux, macOS, and Windows
- Sample programs and drivers used to experiment with and integrate the LiDAR

This code is kept largely in its original structure and used as a dependency.

---

### `docs/`

Engineering documentation for the entire project, including:

- Requirements specifications
- Design specification for the vehicle and subsystems
- System architecture sketches
- Project and time plans
- Technical documentation and after study (postmortem)
- User manual for operating the car and software

These documents capture the full lifecycle of the project, from requirements and planning to implementation and evaluation.

---

## What this project demonstrates

From a portfolio perspective, this project shows the ability to:

- Design and implement a complete embedded and software system for an autonomous vehicle
- Work across multiple abstraction levels, from microcontroller firmware to high level path planning
- Integrate third party hardware and SDKs into a coherent architecture
- Communicate clearly through documentation, specifications, and structured project planning
- Collaborate in a multi person engineering project with well defined roles and responsibilities

