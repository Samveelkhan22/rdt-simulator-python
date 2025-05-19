# RDT Simulator

A Python-based simulation of a Reliable Data Transmission (RDT) layer over an unreliable channel. This project implements a simplified Go-Back-N/Selective Repeat style protocol with pipelining, timeouts, flow‐control, checksums, and cumulative ACKs to reliably transmit arbitrary text data.

---

## Table of Contents

- [Features](#features)  
- [Getting Started](#getting-started)  
  - [Prerequisites](#prerequisites)  
  - [Installation](#installation)  
- [Usage](#usage)  
- [Configuration](#configuration)  
- [Example Output](#example-output)  
- [Project Structure](#project-structure)  
- [License](#license)  

---

## Features

- **Segmented Data**: Splits input text into fixed‐size payload segments.  
- **Pipelining**: Sends multiple un‐ACKed segments up to a flow‐control window.  
- **Timeouts & Retransmissions**: Retransmits timed‐out segments.  
- **Checksums**: Detects corrupted data segments.  
- **Cumulative ACKs**: Acknowledges highest in‐order byte received.  
- **Flow Control**: Limits in‐flight data by window size.  
- **Simulated Unreliability**: Underlying `UnreliableChannel` can drop, delay, reorder, and corrupt segments.

---

## Getting Started

### Prerequisites

- Python 3.6 or later (no external dependencies)

---

## Usage

- Edit rdt_main.py to select which text bundle to send (short vs. longer sample).

- Run the simulation:

```
python rdt_main.py

```

- Press Enter each time you see Press enter to continue... to step through iterations.

- Simulation will print per‐iteration debugging info and final RDT statistics.

---

## Configuration

- Payload size & window size live in rdt_layer.py:

```

DATA_LENGTH = 4                # max chars per segment
FLOW_CONTROL_WIN_SIZE = 15     # window size in characters
TIMEOUT = UnreliableChannel.ITERATIONS_TO_DELAY_PACKETS + 1

```

UnreliableChannel flags in rdt_main.py let you toggle:

- packet drop
- packet reorder
- packet delay
- checksum errors

---

## Example Output
- Short text (“The quick brown fox…”) completes in 5 iterations with no errors.
- Longer JFK Moon Speech sample runs ~200 iterations with full reliability.

---

## Project Structure

- segment.py           # Defines Segment class (seq, ack, checksum)
- unreliable.py        # Simulates drops, delays, reordering, corruption
- rdt_layer.py         # Your implementation of RDT send/receive logic
- rdt_main.py          # Harness that ties client/server layers over two channels
- README.md            # Project overview and instructions


