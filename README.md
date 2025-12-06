# 🕸️ Interactive Graph Algorithm Visualizer

> [Enter URL] https://algorithmlabteampt.streamlit.app/

A web-based educational tool designed to visualize '**Core Graph Traversal Algorithms**' step-by-step. Built with **`Streamlit`** and **`Graphviz`**, this project demonstrates the internal mechanics of graph algorithms including 

**BFS, DFS (with edge classification), Topological Sort, and SCC (Kosaraju's Algorithm)**.

> **Note:** This project was developed as a team assignment for an Algorithm class. The core logic strictly adheres to constraints such as **avoiding Python dictionaries/sets** for graph representation, utilizing **Binary Search** and **Lists** instead to simulate low-level memory management.

## 🌟 Key Features

* **Multi-Mode Support:** Handles both **Directed** and **Undirected** graphs.
* **Step-by-Step Simulation:** Interactive playback controls (Prev/Next) to observe the algorithm's progress.
* **Visual Feedback:** Dynamic coloring for nodes, edges, and active traversal paths.
* **Data Structure Inspection:** View the Adjacency Matrix and Adjacency List (text format) in real-time.
* **Custom Input:** Support for direct text input or `.txt` file uploads for edge lists.

---

## 📂 Project Architecture

The project follows a clean separation of concerns between the Presentation Layer and the Logic Layer.

```bash
📦 Graph-Algo-Visualizer
 ┣ 📜 app.py             # [Presentation Layer] Main Streamlit application handling UI and Rendering.
 ┣ 📜 functions.py       # [Logic Layer] Core algorithms (BFS, DFS, Topo, SCC) and Snapshot generation.
 ┣ 📜 data_manager.py    # [Data Layer] Helper functions for parsing text/file inputs.
 ┗ 📜 requirements.txt   # List of dependencies.
````

### File Roles

| File | Description |
| :--- | :--- |
| **`app.py`** | Acts as the frontend. It manages the **Session State**, renders the graph using **Graphviz**, and handles user interactions (sidebar controls, navigation buttons). It interprets the "snapshots" from the backend to draw the UI. |
| **`functions.py`** | Contains the algorithmic brains. It implements BFS, DFS, Topological Sort, and SCC. **Crucially, it records every step of the algorithm into a `steps` list (snapshots)**, allowing the frontend to "replay" the logic without re-running it. |
| **`data_manager.py`**| Utilities for parsing raw edge lists (e.g., `A B`) into structured node/edge data used by the simulation. |

-----

## 🚀 Supported Algorithms & Visual Elements

### 1\. BFS (Breadth-First Search)

  * **Visualization:** Uses a **Queue (FIFO)**.
  * **Visual Cues:**
      * Nodes show their **Level (L0, L1...)** from the start node.
      * Displays the **Live Adjacency List** for discovered nodes.
  <figure>  
    <img
      width="1908" height="912" alt="image"
      src="https://github.com/user-attachments/assets/9feedc59-77ac-4c3f-aa20-13f28e1a24c3"    
      />  
    <figcaption>Fig 1. BFS Visualization Example</figcaption></figure>
  </figure>
  
### 2\. DFS (Depth-First Search)

  * **Visualization:** Uses a **Stack (LIFO)**.
  * **Edge Classification:**
      * `\<span style="color:\#3498DB"\>`**🟦 Blue Solid:**\</span\> **Tree Edge** (Discovery path).
      * `\<span style="color:\#E74C3C"\>`**🟥 Red Dashed:**\</span\> **Back Edge** (Cycle detection / Ancestor connection).
      * `\<span style="color:\#95A5A6"\>`**⬜ Gray Dotted:**\</span\> **Cross/Forward Edge**.
  * **Visual Cues:** Nodes show their **Depth (D0, D1...)**.
  <figure>  
    <img
      width="1908" height="912" alt="image"
      src="https://github.com/user-attachments/assets/2175299d-d3a8-4911-9871-f56488ce7805" />
    <figcaption>Fig 2. DFS Visualization Example</figcaption>
  </figure>
  
### 3\. Topological Sort

  * **Method:** DFS-based approach (using finishing times).
  * **Visualization:**
      * Detects **Cycles** (shows error if found).
      * Shows the **Result Order** dynamically as nodes are popped from the recursion stack.
      * Displays **Rank (\#1, \#2...)** for sorted nodes.
  <figure>  
    <img
      width="1908" height="912" alt="image"
      src="https://github.com/user-attachments/assets/f9d5e6bc-086a-418b-82c6-322ad173b981" />
    <figcaption>Fig 3. Topological Sort Visualization Example</figcaption>
  </figure>

### 4\. SCC (Strongly Connected Components)

  * **Method:** **Kosaraju's Algorithm** (Two-pass DFS).
  * **Visualization:**
      * **Phase 1:** Fills the stack based on finishing times.
      * **Phase 2:** Performs DFS on the Transpose Graph.
      * **Grouping:** Identified SCCs are colored with distinct **Group Colors (G0, G1...)** for easy differentiation.
  <figure>  
    <img
      width="1908" height="912" alt="image"
      src="https://github.com/user-attachments/assets/35e106eb-a269-4f41-a8b3-da573be10051" />
    <figcaption>Fig 4. SCC Visualization Example</figcaption>
  </figure>
-----

## 🖥️ UI Layout Guide

### 1\. Sidebar (Settings)

  * **Directed Toggle:** Switch between Directed/Undirected graphs.
  * **Input Tab:** Type edge lists manually or upload a `.txt` file.
  * **Algorithm Selector:** Choose the algorithm and the **Start Node**.

### 2\. Main Visualization (Left Column)

  * Renders the interactive graph using `graphviz`.
  * Updates node colors (White → Gray → Mint/Green) and edge styles in real-time.

### 3\. Control Panel (Right Column)

  * **Navigation:** `Prev` / `Next` buttons and a Progress Bar.
  * **Data Structures:** Shows the current state of the **Queue** or **Stack**.
  * **Context Info:**
      * **BFS/DFS:** Shows neighbors of currently active nodes.
      * **Topo Sort:** Shows the sorted result list.
      * **SCC:** Lists the members of identified component groups.
  * **Execution Log:** A scrollable history of algorithmic events (Visiting, Pushing, Popping, Backtracking).

### 4\. Data Inspection (Bottom)

  * Expandable section to view the raw **Adjacency Matrix** and **Adjacency List** representation of the current graph.

-----

## 🛠️ Installation & Usage

### Prerequisites

  * Python 3.8+
  * [Graphviz](https://graphviz.org/download/) installed on your system (required for rendering).

### Steps

1.  **Clone the repository**

    ```bash
    git clone [https://github.com/your-username/graph-algo-visualizer.git](https://github.com/your-username/graph-algo-visualizer.git)
    cd graph-algo-visualizer
    ```

2.  **Install dependencies**

    ```bash
    pip install streamlit graphviz pandas
    ```

3.  **Run the application**

    ```bash
    streamlit run app.py
    ```
