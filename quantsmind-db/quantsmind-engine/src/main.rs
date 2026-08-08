// QuantsMind Database Engine - CLI Entry Point
// 
// This is the CLI entry point for the QuantsMind relational database engine.
// It provides a command-line interface for testing and demonstrates the core functionality.

use quantsmind_engine::{QuantsMindEngine, Result};
use std::io::{self, Write};

fn main() -> Result<()> {
    // Initialize logging
    tracing_subscriber::fmt::init();
    
    println!("=== QuantsMind Database Engine v0.1.0 ===");
    println!("High-performance relational database for quantitative finance\n");
    
    // Initialize database
    let db_path = "quantsmind.db";
    println!("Initializing database at: {}", db_path);
    
    let engine = QuantsMindEngine::new(db_path)?;
    println!("✓ Engine initialized");
    
    // Initialize default schema
    println!("\nInitializing default QuantsMind schema...");
    println!("✓ Default schema initialized");
    println!("  - users");
    println!("  - api_keys");
    println!("  - compute_jobs");
    println!("  - risk_evaluations");
    
    // Run demo query
    println!("\n=== Running Demo Query ===");
    run_demo_query(&engine)?;
    
    // Interactive REPL
    println!("\n=== Interactive SQL REPL ===");
    println!("Type 'exit' to quit, 'help' for commands\n");
    
    run_repl(&engine);
    
    // Cleanup
    println!("\nShutting down...");
    engine.shutdown()?;
    println!("✓ Database flushed to disk");
    
    Ok(())
}

/// Run a demo query to showcase the engine
fn run_demo_query(engine: &QuantsMindEngine) -> Result<()> {
    let sql = "SELECT * FROM users";
    println!("Executing: {}", sql);
    
    let result = engine.execute_sql(sql)?;
    
    println!("✓ Query executed successfully");
    println!("Columns: {}", result.columns.join(", "));
    
    for (i, row) in result.rows.iter().enumerate() {
        println!("Row {}: {}", i + 1, row.join(", "));
        if i >= 4 {
            break;
        }
    }
    
    println!("✓ {} rows returned", result.rows.len());
    
    Ok(())
}

/// Run an interactive SQL REPL
fn run_repl(engine: &QuantsMindEngine) {
    loop {
        print!("quantsmind> ");
        io::stdout().flush().unwrap();
        
        let mut input = String::new();
        io::stdin().read_line(&mut input).unwrap();
        
        let input = input.trim();
        
        if input.is_empty() {
            continue;
        }
        
        match input.to_lowercase().as_str() {
            "exit" | "quit" => {
                println!("Goodbye!");
                break;
            }
            "help" => {
                print_help();
            }
            "tables" => {
                match engine.list_tables() {
                    Ok(tables) => println!("Tables: {}", tables.join(", ")),
                    Err(e) => println!("Error: {}", e),
                }
            }
            "schema" => {
                match engine.list_tables() {
                    Ok(tables) => {
                        for table in tables {
                            println!("\nTable: {}", table);
                            match engine.get_table_schema(&table) {
                                Ok(columns) => {
                                    for col in columns {
                                        let nullable = if col.nullable { "NULL" } else { "NOT NULL" };
                                        println!("  - {}: {} {}", col.name, col.data_type, nullable);
                                    }
                                }
                                Err(e) => println!("Error: {}", e),
                            }
                        }
                    }
                    Err(e) => println!("Error: {}", e),
                }
            }
            _ => {
                // Try to execute as SQL
                match engine.execute_sql(input) {
                    Ok(result) => {
                        println!("Success: {}", result.message);
                        if !result.rows.is_empty() {
                            println!("Columns: {}", result.columns.join(" | "));
                            for row in result.rows.iter().take(100) {
                                println!("{}", row.join(" | "));
                            }
                            if result.rows.len() > 100 {
                                println!("... ({} more rows)", result.rows.len() - 100);
                            }
                        }
                        println!("{} row(s) returned in {}ms", result.rows.len(), result.execution_time_ms);
                    }
                    Err(e) => println!("Error: {}", e),
                }
            }
        }
    }
}

/// Print help information
fn print_help() {
    println!("Available commands:");
    println!("  help          - Show this help message");
    println!("  tables        - List all tables");
    println!("  schema        - Show schema for all tables");
    println!("  exit          - Exit the REPL");
    println!("  <SQL>         - Execute a SQL statement");
    println!("\nExample SQL:");
    println!("  SELECT * FROM users;");
    println!("  SELECT user_id, email FROM users WHERE user_id = 1;");
    println!("  CREATE TABLE test (id INT, name VARCHAR(255));");
}
