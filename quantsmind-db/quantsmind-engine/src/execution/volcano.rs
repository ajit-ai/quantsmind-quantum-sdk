use crate::execution::types::{Tuple, Schema, Value};
use crate::execution::planner::{PhysicalPlan, AggregateExpr};
use std::collections::HashMap;
use thiserror::Error;

/// Errors that can occur during query execution
#[derive(Error, Debug)]
pub enum ExecutorError {
    #[error("Execution error: {0}")]
    ExecutionError(String),
    
    #[error("Type error: {0}")]
    #[allow(dead_code)]
    TypeError(String),
    
    #[error("End of stream")]
    #[allow(dead_code)]
    EndOfStream,
}

/// Result type for executor operations
pub type Result<T> = std::result::Result<T, ExecutorError>;

/// Volcano Executor trait - pull-based iterator model
/// 
/// All executors implement this trait, allowing them to be composed
/// into a query execution pipeline. The next() method is called repeatedly
/// to fetch tuples one at a time.
pub trait Executor: Send + Sync {
    /// Initialize the executor (open any resources)
    fn open(&mut self) -> Result<()>;
    
    /// Get the next tuple from the executor
    /// Returns None when there are no more tuples
    fn next(&mut self) -> Result<Option<Tuple>>;
    
    /// Close the executor and release resources
    fn close(&mut self) -> Result<()>;
    
    /// Get the schema of the output tuples
    fn schema(&self) -> &Schema;
}

/// Sequential Scan Executor - scans all tuples in a table
pub struct SeqScanExecutor {
    #[allow(dead_code)]
    table: String,
    schema: Schema,
    current_page: u32,
    current_slot: u16,
    is_open: bool,
}

impl SeqScanExecutor {
    pub fn new(table: String, schema: Schema) -> Self {
        SeqScanExecutor {
            table,
            schema,
            current_page: 1,
            current_slot: 0,
            is_open: false,
        }
    }
}

impl Executor for SeqScanExecutor {
    fn open(&mut self) -> Result<()> {
        self.is_open = true;
        self.current_page = 1;
        self.current_slot = 0;
        Ok(())
    }
    
    fn next(&mut self) -> Result<Option<Tuple>> {
        if !self.is_open {
            return Err(ExecutorError::ExecutionError("Executor not open".to_string()));
        }
        
        // In a real implementation, this would read from the buffer pool
        // For this simplified version, we'll generate dummy data
        if self.current_page > 10 {
            return Ok(None); // End of scan
        }
        
        // Generate a dummy tuple
        let tuple = Tuple::new(vec![
            Value::Int((self.current_page * 1000 + self.current_slot as u32) as i64),
            Value::Varchar(format!("row_{}_{}", self.current_page, self.current_slot)),
        ]);
        
        self.current_slot += 1;
        if self.current_slot > 100 {
            self.current_slot = 0;
            self.current_page += 1;
        }
        
        Ok(Some(tuple))
    }
    
    fn close(&mut self) -> Result<()> {
        self.is_open = false;
        Ok(())
    }
    
    fn schema(&self) -> &Schema {
        &self.schema
    }
}

/// Filter Executor - filters tuples based on a predicate
pub struct FilterExecutor {
    input: Box<dyn Executor>,
    predicate: String,
    schema: Schema,
}

impl FilterExecutor {
    pub fn new(input: Box<dyn Executor>, predicate: String) -> Self {
        let schema = input.schema().clone();
        FilterExecutor {
            input,
            predicate,
            schema,
        }
    }
    
    /// Evaluate the predicate against a tuple
    fn evaluate_predicate(&self, tuple: &Tuple) -> bool {
        // Simplified predicate evaluation
        // In a real implementation, this would parse and evaluate the expression
        
        if self.predicate.contains(">") {
            let parts: Vec<&str> = self.predicate.split(">").map(|s| s.trim()).collect();
            if parts.len() == 2 {
                if let Some(Value::Int(value)) = tuple.get(0) {
                    if let Ok(threshold) = parts[1].parse::<i64>() {
                        return *value > threshold;
                    }
                }
            }
        }
        
        if self.predicate.contains("=") {
            let parts: Vec<&str> = self.predicate.split("=").map(|s| s.trim()).collect();
            if parts.len() == 2 {
                if let Some(Value::Int(value)) = tuple.get(0) {
                    if let Ok(target) = parts[1].parse::<i64>() {
                        return *value == target;
                    }
                }
            }
        }
        
        true // Default: pass all tuples
    }
}

impl Executor for FilterExecutor {
    fn open(&mut self) -> Result<()> {
        self.input.open()
    }
    
    fn next(&mut self) -> Result<Option<Tuple>> {
        loop {
            match self.input.next()? {
                Some(tuple) => {
                    if self.evaluate_predicate(&tuple) {
                        return Ok(Some(tuple));
                    }
                    // Otherwise, continue to next tuple
                }
                None => return Ok(None),
            }
        }
    }
    
    fn close(&mut self) -> Result<()> {
        self.input.close()
    }
    
    fn schema(&self) -> &Schema {
        &self.schema
    }
}

/// Projection Executor - projects and reorders columns
pub struct ProjectionExecutor {
    input: Box<dyn Executor>,
    column_indices: Vec<usize>,
    schema: Schema,
}

impl ProjectionExecutor {
    pub fn new(input: Box<dyn Executor>, column_indices: Vec<usize>, schema: Schema) -> Self {
        ProjectionExecutor {
            input,
            column_indices,
            schema,
        }
    }
}

impl Executor for ProjectionExecutor {
    fn open(&mut self) -> Result<()> {
        self.input.open()
    }
    
    fn next(&mut self) -> Result<Option<Tuple>> {
        match self.input.next()? {
            Some(tuple) => {
                let projected_values: Vec<Value> = self.column_indices
                    .iter()
                    .filter_map(|&idx| tuple.get(idx).cloned())
                    .collect();
                
                Ok(Some(Tuple::new(projected_values)))
            }
            None => Ok(None),
        }
    }
    
    fn close(&mut self) -> Result<()> {
        self.input.close()
    }
    
    fn schema(&self) -> &Schema {
        &self.schema
    }
}

/// Hash Join Executor - performs hash-based join
pub struct HashJoinExecutor {
    left: Box<dyn Executor>,
    right: Box<dyn Executor>,
    left_key: String,
    right_key: String,
    schema: Schema,
    build_complete: bool,
    hash_table: HashMap<String, Vec<Tuple>>,
    #[allow(dead_code)]
    right_probe_index: usize,
    current_probe_tuples: Vec<Tuple>,
}

impl HashJoinExecutor {
    pub fn new(
        left: Box<dyn Executor>,
        right: Box<dyn Executor>,
        left_key: String,
        right_key: String,
        schema: Schema,
    ) -> Self {
        HashJoinExecutor {
            left,
            right,
            left_key,
            right_key,
            schema,
            build_complete: false,
            hash_table: HashMap::new(),
            right_probe_index: 0,
            current_probe_tuples: Vec::new(),
        }
    }
    
    /// Extract the join key value from a tuple
    fn extract_key(&self, tuple: &Tuple, _key: &str) -> Option<String> {
        // Simplified key extraction
        // In a real implementation, this would resolve column names
        if let Some(value) = tuple.get(0) {
            Some(value.to_string())
        } else {
            None
        }
    }
    
    /// Build hash table from the left input
    fn build_hash_table(&mut self) -> Result<()> {
        self.left.open()?;
        
        while let Some(tuple) = self.left.next()? {
            if let Some(key) = self.extract_key(&tuple, &self.left_key) {
                self.hash_table.entry(key).or_insert_with(Vec::new).push(tuple);
            }
        }
        
        self.left.close()?;
        self.build_complete = true;
        Ok(())
    }
    
    /// Join two tuples
    fn join_tuples(&self, left: &Tuple, right: &Tuple) -> Tuple {
        let mut joined_values = left.values().to_vec();
        joined_values.extend(right.values().to_vec());
        Tuple::new(joined_values)
    }
}

impl Executor for HashJoinExecutor {
    fn open(&mut self) -> Result<()> {
        self.right.open()?;
        self.build_hash_table()
    }
    
    fn next(&mut self) -> Result<Option<Tuple>> {
        if !self.build_complete {
            self.build_hash_table()?;
        }
        
        // First, consume any current probe tuples
        if let Some(left_tuple) = self.current_probe_tuples.pop() {
            if let Some(right_tuple) = self.current_probe_tuples.last() {
                return Ok(Some(self.join_tuples(&left_tuple, right_tuple)));
            }
        }
        
        // Get next tuple from right input
        while let Some(right_tuple) = self.right.next()? {
            if let Some(key) = self.extract_key(&right_tuple, &self.right_key) {
                if let Some(left_tuples) = self.hash_table.get(&key) {
                    self.current_probe_tuples = left_tuples.clone();
                    if let Some(left_tuple) = self.current_probe_tuples.pop() {
                        return Ok(Some(self.join_tuples(&left_tuple, &right_tuple)));
                    }
                }
            }
        }
        
        Ok(None)
    }
    
    fn close(&mut self) -> Result<()> {
        self.right.close()
    }
    
    fn schema(&self) -> &Schema {
        &self.schema
    }
}

/// Aggregate Executor - performs aggregation
pub struct AggregateExecutor {
    input: Box<dyn Executor>,
    group_by: Vec<usize>,
    aggregates: Vec<AggregateExpr>,
    schema: Schema,
    is_open: bool,
    hash_table: HashMap<String, Vec<Value>>,
}

impl AggregateExecutor {
    pub fn new(
        input: Box<dyn Executor>,
        group_by: Vec<usize>,
        aggregates: Vec<AggregateExpr>,
        schema: Schema,
    ) -> Self {
        AggregateExecutor {
            input,
            group_by,
            aggregates,
            schema,
            is_open: false,
            hash_table: HashMap::new(),
        }
    }
    
    /// Extract group key from tuple
    fn extract_group_key(&self, tuple: &Tuple) -> String {
        self.group_by
            .iter()
            .filter_map(|&idx| tuple.get(idx).map(|v| v.to_string()))
            .collect::<Vec<_>>()
            .join("|")
    }
    
    /// Process all input tuples and build aggregation hash table
    fn process_input(&mut self) -> Result<()> {
        self.input.open()?;
        
        while let Some(tuple) = self.input.next()? {
            let key = self.extract_group_key(&tuple);
            
            // Initialize group if not exists
            if !self.hash_table.contains_key(&key) {
                let mut values = Vec::new();
                for _ in &self.aggregates {
                    values.push(Value::Int(0)); // Initialize with 0
                }
                self.hash_table.insert(key.clone(), values);
            }
            
            // Update aggregates (simplified)
            if let Some(values) = self.hash_table.get_mut(&key) {
                for (i, agg) in self.aggregates.iter().enumerate() {
                    match agg {
                        AggregateExpr::Count(_) => {
                            if let Value::Int(count) = &mut values[i] {
                                *count += 1;
                            }
                        }
                        _ => {} // Other aggregates not implemented
                    }
                }
            }
        }
        
        self.input.close()?;
        Ok(())
    }
    
    /// Get keys from hash table in random order
    fn get_keys(&self) -> Vec<String> {
        self.hash_table.keys().cloned().collect()
    }
    
    /// Remove and return a key-value pair from hash table
    fn remove_key(&mut self, key: &str) -> Option<Vec<Value>> {
        self.hash_table.remove(key)
    }
}

impl Executor for AggregateExecutor {
    fn open(&mut self) -> Result<()> {
        self.is_open = true;
        self.process_input()
    }
    
    fn next(&mut self) -> Result<Option<Tuple>> {
        if !self.is_open {
            return Err(ExecutorError::ExecutionError("Executor not open".to_string()));
        }
        
        // Return one group at a time
        if let Some(key) = self.get_keys().pop() {
            if let Some(values) = self.remove_key(&key) {
                let mut tuple_values = Vec::new();
                
                // Add group by columns
                for part in key.split("|") {
                    tuple_values.push(Value::Varchar(part.to_string()));
                }
                
                // Add aggregate values
                tuple_values.extend(values);
                
                Ok(Some(Tuple::new(tuple_values)))
            } else {
                Ok(None)
            }
        } else {
            Ok(None)
        }
    }
    
    fn close(&mut self) -> Result<()> {
        self.is_open = false;
        Ok(())
    }
    
    fn schema(&self) -> &Schema {
        &self.schema
    }
}

/// Sort Executor - sorts tuples
pub struct SortExecutor {
    input: Box<dyn Executor>,
    order_by: Vec<(usize, bool)>,
    schema: Schema,
    buffer: Vec<Tuple>,
    buffer_index: usize,
    is_open: bool,
}

impl SortExecutor {
    pub fn new(input: Box<dyn Executor>, order_by: Vec<(usize, bool)>, schema: Schema) -> Self {
        SortExecutor {
            input,
            order_by,
            schema,
            buffer: Vec::new(),
            buffer_index: 0,
            is_open: false,
        }
    }
    
    /// Compare two tuples based on order specifications
    #[allow(dead_code)]
    fn compare_tuples(&self, a: &Tuple, b: &Tuple) -> std::cmp::Ordering {
        for (col_idx, ascending) in &self.order_by {
            let a_val = a.get(*col_idx);
            let b_val = b.get(*col_idx);
            
            match (a_val, b_val) {
                (Some(Value::Int(a_int)), Some(Value::Int(b_int))) => {
                    let cmp = a_int.cmp(b_int);
                    if cmp != std::cmp::Ordering::Equal {
                        return if *ascending { cmp } else { cmp.reverse() };
                    }
                }
                (Some(Value::Varchar(a_str)), Some(Value::Varchar(b_str))) => {
                    let cmp = a_str.cmp(b_str);
                    if cmp != std::cmp::Ordering::Equal {
                        return if *ascending { cmp } else { cmp.reverse() };
                    }
                }
                _ => continue,
            }
        }
        
        std::cmp::Ordering::Equal
    }
    
    /// Compare two tuples based on order specifications (standalone version for sorting)
    fn compare_tuples_standalone(order_by: &[(usize, bool)], a: &Tuple, b: &Tuple) -> std::cmp::Ordering {
        for (col_idx, ascending) in order_by {
            let a_val = a.get(*col_idx);
            let b_val = b.get(*col_idx);
            
            match (a_val, b_val) {
                (Some(Value::Int(a_int)), Some(Value::Int(b_int))) => {
                    let cmp = a_int.cmp(b_int);
                    if cmp != std::cmp::Ordering::Equal {
                        return if *ascending { cmp } else { cmp.reverse() };
                    }
                }
                (Some(Value::Varchar(a_str)), Some(Value::Varchar(b_str))) => {
                    let cmp = a_str.cmp(b_str);
                    if cmp != std::cmp::Ordering::Equal {
                        return if *ascending { cmp } else { cmp.reverse() };
                    }
                }
                _ => continue,
            }
        }
        
        std::cmp::Ordering::Equal
    }
}

impl Executor for SortExecutor {
    fn open(&mut self) -> Result<()> {
        self.is_open = true;
        self.input.open()?;
        
        // Load all tuples into buffer
        while let Some(tuple) = self.input.next()? {
            self.buffer.push(tuple);
        }
        
        self.input.close()?;
        
        // Sort the buffer
        let order_by = self.order_by.clone();
        self.buffer.sort_by(|a, b| Self::compare_tuples_standalone(&order_by, a, b));
        
        Ok(())
    }
    
    fn next(&mut self) -> Result<Option<Tuple>> {
        if !self.is_open {
            return Err(ExecutorError::ExecutionError("Executor not open".to_string()));
        }
        
        if self.buffer_index < self.buffer.len() {
            let tuple = self.buffer[self.buffer_index].clone();
            self.buffer_index += 1;
            Ok(Some(tuple))
        } else {
            Ok(None)
        }
    }
    
    fn close(&mut self) -> Result<()> {
        self.is_open = false;
        self.buffer.clear();
        self.buffer_index = 0;
        Ok(())
    }
    
    fn schema(&self) -> &Schema {
        &self.schema
    }
}

/// Limit Executor - limits the number of tuples returned
pub struct LimitExecutor {
    input: Box<dyn Executor>,
    limit: usize,
    count: usize,
    schema: Schema,
}

impl LimitExecutor {
    pub fn new(input: Box<dyn Executor>, limit: usize, schema: Schema) -> Self {
        LimitExecutor {
            input,
            limit,
            count: 0,
            schema,
        }
    }
}

impl Executor for LimitExecutor {
    fn open(&mut self) -> Result<()> {
        self.count = 0;
        self.input.open()
    }
    
    fn next(&mut self) -> Result<Option<Tuple>> {
        if self.count >= self.limit {
            return Ok(None);
        }
        
        match self.input.next()? {
            Some(tuple) => {
                self.count += 1;
                Ok(Some(tuple))
            }
            None => Ok(None),
        }
    }
    
    fn close(&mut self) -> Result<()> {
        self.input.close()
    }
    
    fn schema(&self) -> &Schema {
        &self.schema
    }
}

/// Executor builder - creates executor tree from physical plan
pub struct ExecutorBuilder;

impl ExecutorBuilder {
    /// Build an executor tree from a physical plan
    pub fn build(plan: PhysicalPlan) -> Result<Box<dyn Executor>> {
        match plan {
            PhysicalPlan::SeqScan { table, schema } => {
                Ok(Box::new(SeqScanExecutor::new(table, schema)))
            }
            PhysicalPlan::IndexScan { table, index: _, condition: _, schema } => {
                // For simplicity, use SeqScan even for IndexScan
                Ok(Box::new(SeqScanExecutor::new(table, schema)))
            }
            PhysicalPlan::Filter { input, predicate } => {
                let child = Self::build(*input)?;
                Ok(Box::new(FilterExecutor::new(child, predicate)))
            }
            PhysicalPlan::Projection { input, column_indices, schema } => {
                let child = Self::build(*input)?;
                Ok(Box::new(ProjectionExecutor::new(child, column_indices, schema)))
            }
            PhysicalPlan::HashJoin { left, right, left_key, right_key, join_type: _ } => {
                let left_child = Self::build(*left)?;
                let right_child = Self::build(*right)?;
                let schema = left_child.schema().clone();
                Ok(Box::new(HashJoinExecutor::new(left_child, right_child, left_key, right_key, schema)))
            }
            PhysicalPlan::NestedLoopJoin { left, right, condition: _, join_type: _ } => {
                // For simplicity, use HashJoin
                let left_child = Self::build(*left)?;
                let right_child = Self::build(*right)?;
                let left_key = "key".to_string();
                let right_key = "key".to_string();
                let schema = left_child.schema().clone();
                Ok(Box::new(HashJoinExecutor::new(left_child, right_child, left_key, right_key, schema)))
            }
            PhysicalPlan::Aggregate { input, group_by, aggregates } => {
                let child = Self::build(*input)?;
                let schema = child.schema().clone();
                Ok(Box::new(AggregateExecutor::new(child, group_by, aggregates, schema)))
            }
            PhysicalPlan::Sort { input, order_by } => {
                let child = Self::build(*input)?;
                let schema = child.schema().clone();
                Ok(Box::new(SortExecutor::new(child, order_by, schema)))
            }
            PhysicalPlan::Limit { input, limit } => {
                let child = Self::build(*input)?;
                let schema = child.schema().clone();
                Ok(Box::new(LimitExecutor::new(child, limit, schema)))
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_seq_scan_executor() {
        let mut schema = Schema::new();
        schema.add_column("id".to_string(), crate::execution::types::DataType::Int, false);
        schema.add_column("name".to_string(), crate::execution::types::DataType::Varchar(255), true);
        
        let mut executor = SeqScanExecutor::new("test".to_string(), schema);
        
        executor.open().unwrap();
        
        let mut count = 0;
        while let Some(_) = executor.next().unwrap() {
            count += 1;
            if count >= 5 {
                break;
            }
        }
        
        assert_eq!(count, 5);
        executor.close().unwrap();
    }

    #[test]
    fn test_filter_executor() {
        let mut schema = Schema::new();
        schema.add_column("id".to_string(), crate::execution::types::DataType::Int, false);
        
        let scan = Box::new(SeqScanExecutor::new("test".to_string(), schema.clone()));
        let mut filter = FilterExecutor::new(scan, "id > 5000".to_string());
        
        filter.open().unwrap();
        
        let mut count = 0;
        while let Some(tuple) = filter.next().unwrap() {
            if let Some(Value::Int(id)) = tuple.get(0) {
                assert!(*id > 5000);
            }
            count += 1;
            if count >= 5 {
                break;
            }
        }
        
        filter.close().unwrap();
    }

    #[test]
    fn test_projection_executor() {
        let mut schema = Schema::new();
        schema.add_column("id".to_string(), crate::execution::types::DataType::Int, false);
        schema.add_column("name".to_string(), crate::execution::types::DataType::Varchar(255), true);
        
        let scan = Box::new(SeqScanExecutor::new("test".to_string(), schema.clone()));
        let mut proj = ProjectionExecutor::new(scan, vec![0], schema.clone());
        
        proj.open().unwrap();
        
        if let Some(tuple) = proj.next().unwrap() {
            assert_eq!(tuple.len(), 1);
        }
        
        proj.close().unwrap();
    }

    #[test]
    fn test_limit_executor() {
        let mut schema = Schema::new();
        schema.add_column("id".to_string(), crate::execution::types::DataType::Int, false);
        
        let scan = Box::new(SeqScanExecutor::new("test".to_string(), schema.clone()));
        let mut limit = LimitExecutor::new(scan, 3, schema);
        
        limit.open().unwrap();
        
        let mut count = 0;
        while let Some(_) = limit.next().unwrap() {
            count += 1;
        }
        
        assert_eq!(count, 3);
        limit.close().unwrap();
    }
}
