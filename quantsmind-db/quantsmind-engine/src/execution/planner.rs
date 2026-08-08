use crate::execution::parser::{ASTNode, SelectNode, JoinType};
use crate::execution::types::{Schema, DataType};
use thiserror::Error;

/// Errors that can occur during query planning
#[derive(Error, Debug)]
pub enum PlannerError {
    #[error("Table not found: {0}")]
    #[allow(dead_code)]
    TableNotFound(String),
    
    #[error("Column not found: {0}")]
    ColumnNotFound(String),
    
    #[error("Invalid query: {0}")]
    InvalidQuery(String),
    
    #[error("Type mismatch: {0}")]
    TypeMismatch(String),
}

/// Result type for planning operations
pub type Result<T> = std::result::Result<T, PlannerError>;

/// Logical query plan node
#[derive(Debug, Clone)]
pub enum LogicalPlan {
    /// Scan a table
    Scan {
        table: String,
        schema: Schema,
    },
    /// Filter rows
    Filter {
        input: Box<LogicalPlan>,
        condition: String, // Simplified condition
    },
    /// Project columns
    Project {
        input: Box<LogicalPlan>,
        columns: Vec<String>,
        schema: Schema,
    },
    /// Join two relations
    Join {
        left: Box<LogicalPlan>,
        right: Box<LogicalPlan>,
        join_type: JoinType,
        condition: String,
    },
    /// Aggregate
    Aggregate {
        input: Box<LogicalPlan>,
        group_by: Vec<String>,
        aggregates: Vec<String>,
    },
    /// Sort
    Sort {
        input: Box<LogicalPlan>,
        order_by: Vec<String>,
    },
    /// Limit
    Limit {
        input: Box<LogicalPlan>,
        limit: usize,
    },
}

/// Physical query plan node
#[derive(Debug, Clone)]
pub enum PhysicalPlan {
    /// Sequential scan
    SeqScan {
        table: String,
        schema: Schema,
    },
    /// Index scan
    #[allow(dead_code)]
    IndexScan {
        table: String,
        index: String,
        condition: String,
        schema: Schema,
    },
    /// Filter
    Filter {
        input: Box<PhysicalPlan>,
        predicate: String,
    },
    /// Projection
    Projection {
        input: Box<PhysicalPlan>,
        column_indices: Vec<usize>,
        schema: Schema,
    },
    /// Hash join
    HashJoin {
        left: Box<PhysicalPlan>,
        right: Box<PhysicalPlan>,
        left_key: String,
        right_key: String,
        #[allow(dead_code)]
        join_type: JoinType,
    },
    /// Nested loop join
    NestedLoopJoin {
        left: Box<PhysicalPlan>,
        right: Box<PhysicalPlan>,
        condition: String,
        #[allow(dead_code)]
        join_type: JoinType,
    },
    /// Aggregate
    Aggregate {
        input: Box<PhysicalPlan>,
        group_by: Vec<usize>,
        aggregates: Vec<AggregateExpr>,
    },
    /// Sort
    Sort {
        input: Box<PhysicalPlan>,
        order_by: Vec<(usize, bool)>, // (column_index, ascending)
    },
    /// Limit
    Limit {
        input: Box<PhysicalPlan>,
        limit: usize,
    },
}

/// Aggregate expression
#[derive(Debug, Clone)]
pub enum AggregateExpr {
    #[allow(dead_code)]
    Count(String),
    #[allow(dead_code)]
    Sum(String),
    #[allow(dead_code)]
    Avg(String),
    #[allow(dead_code)]
    Min(String),
    #[allow(dead_code)]
    Max(String),
}

/// Query Planner - converts logical plans to physical plans
pub struct QueryPlanner;

impl QueryPlanner {
    /// Convert an AST to a logical plan
    pub fn ast_to_logical(ast: &ASTNode) -> Result<LogicalPlan> {
        match ast {
            ASTNode::Select(select) => Self::select_to_logical(select),
            ASTNode::Insert(insert) => Self::insert_to_logical(insert),
            ASTNode::Update(update) => Self::update_to_logical(update),
            ASTNode::Delete(delete) => Self::delete_to_logical(delete),
            ASTNode::CreateTable(create) => Self::create_table_to_logical(create),
            ASTNode::DropTable(drop) => Self::drop_table_to_logical(drop),
        }
    }
    
    /// Convert SELECT to logical plan
    fn select_to_logical(select: &SelectNode) -> Result<LogicalPlan> {
        // Start with a scan
        let table = select.from.as_ref()
            .ok_or_else(|| PlannerError::InvalidQuery("Missing FROM clause".to_string()))?;
        
        let schema = Self::get_table_schema(table)?;
        let mut plan = LogicalPlan::Scan {
            table: table.clone(),
            schema: schema.clone(),
        };
        
        // Add joins
        for join in &select.joins {
            let right_schema = Self::get_table_schema(&join.table)?;
            let right_plan = LogicalPlan::Scan {
                table: join.table.clone(),
                schema: right_schema,
            };
            
            plan = LogicalPlan::Join {
                left: Box::new(plan),
                right: Box::new(right_plan),
                join_type: join.join_type,
                condition: join.condition.as_ref()
                    .map(|c| c.to_string())
                    .unwrap_or_else(|| "true".to_string()),
            };
        }
        
        // Add WHERE filter
        if let Some(where_clause) = &select.where_clause {
            plan = LogicalPlan::Filter {
                input: Box::new(plan),
                condition: where_clause.to_string(),
            };
        }
        
        // Add projection
        if !select.columns.is_empty() {
            let columns: Vec<String> = select.columns.iter()
                .filter_map(|item| {
                    match item {
                        sqlparser::ast::SelectItem::UnnamedExpr(expr) => Some(expr.to_string()),
                        sqlparser::ast::SelectItem::ExprWithAlias { expr, .. } => Some(expr.to_string()),
                        _ => None,
                    }
                })
                .collect();
            
            let projected_schema = Self::project_schema(&schema, &columns)?;
            plan = LogicalPlan::Project {
                input: Box::new(plan),
                columns,
                schema: projected_schema,
            };
        }
        
        // Add GROUP BY and HAVING
        if !select.group_by.is_empty() {
            let group_by: Vec<String> = select.group_by.iter().map(|e| e.to_string()).collect();
            let aggregates: Vec<String> = select.having.as_ref()
                .map(|h| vec![h.to_string()])
                .unwrap_or_default();
            
            plan = LogicalPlan::Aggregate {
                input: Box::new(plan),
                group_by,
                aggregates,
            };
        }
        
        // Add ORDER BY
        if !select.order_by.is_empty() {
            plan = LogicalPlan::Sort {
                input: Box::new(plan),
                order_by: select.order_by.iter().map(|ob| ob.expr.to_string()).collect(),
            };
        }
        
        // Add LIMIT
        if let Some(limit) = select.limit {
            plan = LogicalPlan::Limit {
                input: Box::new(plan),
                limit: limit as usize,
            };
        }
        
        Ok(plan)
    }
    
    /// Convert INSERT to logical plan
    fn insert_to_logical(insert: &crate::execution::parser::InsertNode) -> Result<LogicalPlan> {
        let schema = Self::get_table_schema(&insert.table)?;
        
        // For INSERT, we return a special plan that includes the values
        // In a real implementation, this would be more sophisticated
        Ok(LogicalPlan::Scan {
            table: insert.table.clone(),
            schema,
        })
    }
    
    /// Convert UPDATE to logical plan
    fn update_to_logical(update: &crate::execution::parser::UpdateNode) -> Result<LogicalPlan> {
        let schema = Self::get_table_schema(&update.table)?;
        let mut plan = LogicalPlan::Scan {
            table: update.table.clone(),
            schema: schema.clone(),
        };
        
        if let Some(where_clause) = &update.where_clause {
            plan = LogicalPlan::Filter {
                input: Box::new(plan),
                condition: where_clause.to_string(),
            };
        }
        
        Ok(plan)
    }
    
    /// Convert DELETE to logical plan
    fn delete_to_logical(delete: &crate::execution::parser::DeleteNode) -> Result<LogicalPlan> {
        let schema = Self::get_table_schema(&delete.table)?;
        let mut plan = LogicalPlan::Scan {
            table: delete.table.clone(),
            schema: schema.clone(),
        };
        
        if let Some(where_clause) = &delete.where_clause {
            plan = LogicalPlan::Filter {
                input: Box::new(plan),
                condition: where_clause.to_string(),
            };
        }
        
        Ok(plan)
    }
    
    /// Convert CREATE TABLE to logical plan
    fn create_table_to_logical(create: &crate::execution::parser::CreateTableNode) -> Result<LogicalPlan> {
        let mut schema = Schema::new();
        
        for column in &create.columns {
            let data_type = Self::parse_data_type(&column.data_type)?;
            schema.add_column(column.name.clone(), data_type, column.nullable);
        }
        
        Ok(LogicalPlan::Scan {
            table: create.table.clone(),
            schema,
        })
    }
    
    /// Convert DROP TABLE to logical plan
    fn drop_table_to_logical(drop: &crate::execution::parser::DropTableNode) -> Result<LogicalPlan> {
        Ok(LogicalPlan::Scan {
            table: drop.table.clone(),
            schema: Schema::new(),
        })
    }
    
    /// Convert logical plan to physical plan
    pub fn logical_to_physical(logical: &LogicalPlan) -> Result<PhysicalPlan> {
        match logical {
            LogicalPlan::Scan { table, schema } => {
                // Decide between SeqScan and IndexScan based on conditions
                // For simplicity, we use SeqScan
                Ok(PhysicalPlan::SeqScan {
                    table: table.clone(),
                    schema: schema.clone(),
                })
            }
            LogicalPlan::Filter { input, condition } => {
                let physical_input = Self::logical_to_physical(input)?;
                Ok(PhysicalPlan::Filter {
                    input: Box::new(physical_input),
                    predicate: condition.clone(),
                })
            }
            LogicalPlan::Project { input, columns, schema } => {
                let physical_input = Self::logical_to_physical(input)?;
                let column_indices = Self::resolve_column_indices(schema, columns)?;
                Ok(PhysicalPlan::Projection {
                    input: Box::new(physical_input),
                    column_indices,
                    schema: schema.clone(),
                })
            }
            LogicalPlan::Join { left, right, join_type, condition } => {
                let physical_left = Self::logical_to_physical(left)?;
                let physical_right = Self::logical_to_physical(right)?;
                
                // Decide between HashJoin and NestedLoopJoin
                // For simplicity, we use HashJoin for equijoins
                if condition.contains("=") {
                    // Extract join keys (simplified)
                    let (left_key, right_key) = Self::extract_join_keys(condition)?;
                    Ok(PhysicalPlan::HashJoin {
                        left: Box::new(physical_left),
                        right: Box::new(physical_right),
                        left_key,
                        right_key,
                        join_type: *join_type,
                    })
                } else {
                    Ok(PhysicalPlan::NestedLoopJoin {
                        left: Box::new(physical_left),
                        right: Box::new(physical_right),
                        condition: condition.clone(),
                        join_type: *join_type,
                    })
                }
            }
            LogicalPlan::Aggregate { input, group_by, aggregates } => {
                let physical_input = Self::logical_to_physical(input)?;
                let group_by_indices = Self::resolve_column_indices(&physical_input.get_schema(), group_by)?;
                let aggregate_exprs = Self::parse_aggregates(aggregates)?;
                
                Ok(PhysicalPlan::Aggregate {
                    input: Box::new(physical_input),
                    group_by: group_by_indices,
                    aggregates: aggregate_exprs,
                })
            }
            LogicalPlan::Sort { input, order_by } => {
                let physical_input = Self::logical_to_physical(input)?;
                let schema = physical_input.get_schema();
                let order_indices = Self::resolve_order_indices(&schema, order_by)?;
                
                Ok(PhysicalPlan::Sort {
                    input: Box::new(physical_input),
                    order_by: order_indices,
                })
            }
            LogicalPlan::Limit { input, limit } => {
                let physical_input = Self::logical_to_physical(input)?;
                Ok(PhysicalPlan::Limit {
                    input: Box::new(physical_input),
                    limit: *limit,
                })
            }
        }
    }
    
    /// Get table schema (simplified - in real implementation would query catalog)
    fn get_table_schema(_table: &str) -> Result<Schema> {
        // For testing, return a dummy schema
        let mut schema = Schema::new();
        schema.add_column("id".to_string(), DataType::Int, false);
        schema.add_column("name".to_string(), DataType::Varchar(255), true);
        Ok(schema)
    }
    
    /// Project schema to selected columns
    fn project_schema(schema: &Schema, columns: &[String]) -> Result<Schema> {
        let mut new_schema = Schema::new();
        
        for column in columns {
            if let Some(index) = schema.find_column(column) {
                let name = schema.get_column_name(index).unwrap().to_string();
                let data_type = schema.get_column_type(index).unwrap().clone();
                let nullable = schema.is_nullable(index).unwrap();
                new_schema.add_column(name, data_type, nullable);
            } else {
                return Err(PlannerError::ColumnNotFound(column.clone()));
            }
        }
        
        Ok(new_schema)
    }
    
    /// Resolve column names to indices
    fn resolve_column_indices(schema: &Schema, columns: &[String]) -> Result<Vec<usize>> {
        let mut indices = Vec::new();
        
        for column in columns {
            if let Some(index) = schema.find_column(column) {
                indices.push(index);
            } else {
                return Err(PlannerError::ColumnNotFound(column.clone()));
            }
        }
        
        Ok(indices)
    }
    
    /// Resolve ORDER BY columns to indices
    fn resolve_order_indices(schema: &Schema, order_by: &[String]) -> Result<Vec<(usize, bool)>> {
        let mut indices = Vec::new();
        
        for column in order_by {
            let ascending = !column.starts_with("-");
            let clean_column = if column.starts_with("-") {
                &column[1..]
            } else {
                column.as_str()
            };
            
            if let Some(index) = schema.find_column(clean_column) {
                indices.push((index, ascending));
            } else {
                return Err(PlannerError::ColumnNotFound(clean_column.to_string()));
            }
        }
        
        Ok(indices)
    }
    
    /// Extract join keys from condition (simplified)
    fn extract_join_keys(condition: &str) -> Result<(String, String)> {
        // Parse "left.key = right.key" format
        let parts: Vec<&str> = condition.split('=').map(|s| s.trim()).collect();
        if parts.len() == 2 {
            Ok((parts[0].to_string(), parts[1].to_string()))
        } else {
            Err(PlannerError::InvalidQuery("Invalid join condition".to_string()))
        }
    }
    
    /// Parse aggregate expressions
    fn parse_aggregates(aggregates: &[String]) -> Result<Vec<AggregateExpr>> {
        let mut exprs = Vec::new();
        
        for agg in aggregates {
            let expr = if agg.starts_with("COUNT(") {
                let column = agg.trim_start_matches("COUNT(").trim_end_matches(")");
                AggregateExpr::Count(column.to_string())
            } else if agg.starts_with("SUM(") {
                let column = agg.trim_start_matches("SUM(").trim_end_matches(")");
                AggregateExpr::Sum(column.to_string())
            } else if agg.starts_with("AVG(") {
                let column = agg.trim_start_matches("AVG(").trim_end_matches(")");
                AggregateExpr::Avg(column.to_string())
            } else if agg.starts_with("MIN(") {
                let column = agg.trim_start_matches("MIN(").trim_end_matches(")");
                AggregateExpr::Min(column.to_string())
            } else if agg.starts_with("MAX(") {
                let column = agg.trim_start_matches("MAX(").trim_end_matches(")");
                AggregateExpr::Max(column.to_string())
            } else {
                return Err(PlannerError::InvalidQuery(format!("Unknown aggregate: {}", agg)));
            };
            
            exprs.push(expr);
        }
        
        Ok(exprs)
    }
    
    /// Parse data type string to DataType enum
    fn parse_data_type(type_str: &str) -> Result<DataType> {
        match type_str.to_uppercase().as_str() {
            "INT" | "INTEGER" => Ok(DataType::Int),
            "VARCHAR" | "TEXT" => Ok(DataType::Varchar(255)),
            "FLOAT" | "DOUBLE" => Ok(DataType::Float),
            "BOOLEAN" | "BOOL" => Ok(DataType::Boolean),
            "TIMESTAMP" => Ok(DataType::Timestamp),
            "UUID" => Ok(DataType::UUID),
            "NUMERIC" | "DECIMAL" => Ok(DataType::Numeric(38, 10)),
            _ => Err(PlannerError::TypeMismatch(format!("Unknown type: {}", type_str))),
        }
    }
}

impl PhysicalPlan {
    /// Get the schema of the output of this plan
    pub fn get_schema(&self) -> Schema {
        match self {
            PhysicalPlan::SeqScan { schema, .. } => schema.clone(),
            PhysicalPlan::IndexScan { schema, .. } => schema.clone(),
            PhysicalPlan::Filter { input, .. } => input.get_schema(),
            PhysicalPlan::Projection { schema, .. } => schema.clone(),
            PhysicalPlan::HashJoin { left, right, .. } => {
                // Combine schemas from both sides
                let left_schema = left.get_schema();
                let right_schema = right.get_schema();
                let mut combined = Schema::new();
                
                for (i, name) in left_schema.columns().iter().enumerate() {
                    combined.add_column(
                        format!("left.{}", name),
                        left_schema.get_column_type(i).unwrap().clone(),
                        left_schema.is_nullable(i).unwrap(),
                    );
                }
                
                for (i, name) in right_schema.columns().iter().enumerate() {
                    combined.add_column(
                        format!("right.{}", name),
                        right_schema.get_column_type(i).unwrap().clone(),
                        right_schema.is_nullable(i).unwrap(),
                    );
                }
                
                combined
            }
            PhysicalPlan::NestedLoopJoin { left, right, .. } => {
                let left_schema = left.get_schema();
                let right_schema = right.get_schema();
                let mut combined = Schema::new();
                
                for (i, name) in left_schema.columns().iter().enumerate() {
                    combined.add_column(
                        format!("left.{}", name),
                        left_schema.get_column_type(i).unwrap().clone(),
                        left_schema.is_nullable(i).unwrap(),
                    );
                }
                
                for (i, name) in right_schema.columns().iter().enumerate() {
                    combined.add_column(
                        format!("right.{}", name),
                        right_schema.get_column_type(i).unwrap().clone(),
                        right_schema.is_nullable(i).unwrap(),
                    );
                }
                
                combined
            }
            PhysicalPlan::Aggregate { input, .. } => input.get_schema(),
            PhysicalPlan::Sort { input, .. } => input.get_schema(),
            PhysicalPlan::Limit { input, .. } => input.get_schema(),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_simple_select_plan() {
        let ast = ASTNode::Select(SelectNode {
            columns: vec![],
            from: Some("users".to_string()),
            where_clause: None,
            joins: vec![],
            group_by: vec![],
            having: None,
            order_by: vec![],
            limit: None,
        });
        
        let logical = QueryPlanner::ast_to_logical(&ast);
        assert!(logical.is_ok());
        
        let physical = QueryPlanner::logical_to_physical(&logical.unwrap());
        assert!(physical.is_ok());
    }

    #[test]
    fn test_data_type_parsing() {
        assert!(matches!(QueryPlanner::parse_data_type("INT"), Ok(DataType::Int)));
        assert!(matches!(QueryPlanner::parse_data_type("VARCHAR"), Ok(DataType::Varchar(_))));
        assert!(matches!(QueryPlanner::parse_data_type("BOOLEAN"), Ok(DataType::Boolean)));
    }
}
