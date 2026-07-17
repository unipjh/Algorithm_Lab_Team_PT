<!-- problem-first-summary:start -->
**Huge Problem(Pain Point):** 그래프 탐색 알고리즘은 최종 결과만 보면 큐·스택·간선 분류의 변화를 이해하기 어렵다.

**솔루션 한 줄 정의:** BFS·DFS·위상 정렬·SCC의 내부 상태를 단계별로 재생하는 대화형 시각화 도구다.

**현재 상태:** 팀 과제 사례 연구

**문제 해결 중심의 사고 흐름**

1. **관찰** — 교재의 정적 그래프만으로는 탐색 순서와 자료구조 상태가 왜 바뀌는지 따라가기 어려웠다.
2. **선택** — 각 알고리즘을 상태 스냅샷의 연속으로 만들고 이전·다음 단계로 재생하도록 설계했다.
3. **구현** — Streamlit과 Graphviz로 노드·간선·큐·스택·SCC 그룹을 단계별 색상과 레이블로 표현했다.
4. **검증과 한계** — 배포 URL과 BFS·DFS·위상 정렬·Kosaraju SCC 흐름이 README에 기록되어 있다. 팀 내 개인 기여 범위는 추가 확인이 필요하다.
<!-- problem-first-summary:end -->

---
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
     width="1274" height="682" alt="image" 
     src="https://github.com/user-attachments/assets/4d0e0d61-12c8-4fb5-afab-5df118e41db3" />
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
   <img width="1273" height="677" alt="image" 
    src="https://github.com/user-attachments/assets/e59917ae-8af8-4663-94be-fdebfff1e0a0" />
    <figcaption>Fig 2. DFS Visualization Example</figcaption>
  </figure>
  
### 3\. Topological Sort

  * **Method:** DFS-based approach (using finishing times).
  * **Visualization:**
      * Detects **Cycles** (shows error if found).
      * Shows the **Result Order** dynamically as nodes are popped from the recursion stack.
      * Displays **Rank (\#1, \#2...)** for sorted nodes.
  <figure>  
   <img width="1268" height="665" alt="image" 
    src="https://github.com/user-attachments/assets/5b03a39a-95b2-4346-9557-7f149acb7787" />
    <figcaption>Fig 3. Topological Sort Visualization Example</figcaption>
  </figure>

### 4\. SCC (Strongly Connected Components)

  * **Method:** **Kosaraju's Algorithm** (Two-pass DFS).
  * **Visualization:**
      * **Phase 1:** Fills the stack based on finishing times.
      * **Phase 2:** Performs DFS on the Transpose Graph.
      * **Grouping:** Identified SCCs are colored with distinct **Group Colors (G0, G1...)** for easy differentiation.
  <figure>  
    <img width="1269" height="674" alt="image" 
     src="https://github.com/user-attachments/assets/317eb2d9-adca-4114-8049-e61fa6d60b60" />
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
  * **Components & Tree Edges:** Shows the number of connected components and edges
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
