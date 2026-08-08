# QuantsMind Database System & Visual Studio

A high-performance relational database engine and visual development studio optimized for quantitative finance metadata, trade execution tracking, and risk analytics orchestrations.

## 🚀 Quick Start

### Prerequisites

**For Windows:**
- [Rust](https://rustup.rs/) (1.70 or later)
- [Node.js](https://nodejs.org/) (18 or later)
- [npm](https://www.npmjs.com/) (comes with Node.js)

**For Linux:**
- Rust: `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`
- Node.js: `curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - && sudo apt-get install -y nodejs`
- Build tools: `sudo apt-get install build-essential libwebkit2gtk-4.0-dev libssl-dev libgtk-3-dev libayatana-appindicator3-dev librsvg2-dev`

### Installation

1. **Run the setup script:**

   **Windows:**
   ```bash
   setup.bat
   ```

   **Linux:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

2. **Run the engine (CLI mode):**
   ```bash
   cd quantsmind-engine
   cargo run --release
   ```

3. **Run the studio (GUI mode):**
   ```bash
   cd quantsmind-studio
   npm run tauri dev
   ```

## 📁 Project Structure

```
quantsmind-db/
├── quantsmind-engine/          # Rust Database Core Engine
│   ├── Cargo.toml
│   └── src/
│       ├── main.rs              # CLI entry point with REPL
│       ├── storage/             # Page architecture, disk I/O, buffer pool
│       ├── index/               # B+ Tree indexing
│       ├── concurrency/         # Lock management and WAL
│       ├── catalog/             # System catalog and schema
│       ├── execution/           # Query types, parser, planner, executor
│       └── server/              # gRPC/IPC API handlers
│
└── quantsmind-studio/          # Tauri v2 + React Studio GUI
    ├── src-tauri/              # Rust desktop wrapper
    ├── package.json
    └── src/
        ├── App.tsx              # Studio shell & workspace layout
        ├── components/          # React Flow canvas, query editor, data grid
        ├── types/               # Schema type definitions
        └── utils/               # DDL compiler utilities
```

## 🗄️ Default Schema

The system initializes with the QuantsMind quantitative finance schema:

```sql
-- Identity & Access Management
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    organization VARCHAR(100) NOT NULL,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE api_keys (
    key_id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    key_hash VARCHAR(64) NOT NULL,
    rate_limit_rpm INT NOT NULL,
    CONSTRAINT fk_api_keys_user_id FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Workload Orchestration & Risk Engine
CREATE TABLE compute_jobs (
    job_id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    target_backend VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    execution_time_ms INT,
    created_at TIMESTAMP NOT NULL,
    CONSTRAINT fk_compute_jobs_user_id FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE risk_evaluations (
    eval_id UUID PRIMARY KEY,
    job_id UUID NOT NULL,
    portfolio_id UUID NOT NULL,
    var_99 NUMERIC(20,6) NOT NULL,
    sharpe_ratio NUMERIC(10,4) NOT NULL,
    max_drawdown NUMERIC(20,6) NOT NULL,
    evaluated_at TIMESTAMP NOT NULL,
    CONSTRAINT fk_risk_evaluations_job_id FOREIGN KEY (job_id) REFERENCES compute_jobs(job_id)
);
```

## �️ Technical Details

### Storage Engine
- **Page Size**: 8KB (8192 bytes)
- **Page Header**: 32 bytes (page_id, lsn, slot_count, free_space_pointer, flags)
- **Slotted Page**: Variable-length tuples with slot array growing forward
- **Buffer Pool**: 1024 frames by default (8MB memory), Clock replacement

### Query Execution
- **Parser**: sqlparser-rs for SQL parsing
- **Planner**: Logical plan → Physical plan transformation
- **Executor**: Volcano iterator model (pull-based)
- **Operators**: SeqScan, IndexScan, Filter, Projection, HashJoin, Aggregate

### Concurrency
- **Locking**: Strict Two-Phase Locking (SS2PL)
- **Granularity**: Table and Row-level locks
- **Deadlock Detection**: Wait-for graph cycle detection
- **WAL**: Write-Ahead Logging with ARIES recovery

## 📚 Features

### Rust Engine
- ✅ 8KB binary page architecture with slotted page structure
- ✅ Buffer pool manager with Clock replacement algorithm
- ✅ B+ Tree indexing for fast key lookups
- ✅ Write-Ahead Logging (WAL) with ARIES recovery
- ✅ Strict Two-Phase Locking (SS2PL) with deadlock detection
- ✅ SQL parser using sqlparser-rs
- ✅ Volcano iterator execution model
- ✅ gRPC/IPC server API

### React Studio
- ✅ Visual schema designer with drag-and-drop tables
- ✅ Foreign key relationship visualization
- ✅ Real-time DDL generation (PostgreSQL-compatible)
- ✅ Monaco SQL editor with syntax highlighting
- ✅ Virtualized data grid with sorting/filtering
- ✅ CSV export functionality
- ✅ Tauri desktop application

## � License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Built with [Rust](https://www.rust-lang.org/)
- Powered by [Tauri](https://tauri.app/)
- UI with [React](https://reactjs.org/) and [React Flow](https://reactflow.dev/)
- SQL parsing with [sqlparser-rs](https://github.com/sqlparser-rs/sqlparser-rs)
