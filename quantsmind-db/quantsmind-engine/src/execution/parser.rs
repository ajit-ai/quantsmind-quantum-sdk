use sqlparser::parser::Parser;
use sqlparser::ast::{Statement, Query, SetExpr, Select, SelectItem, Expr};
use sqlparser::dialect::GenericDialect;
use thiserror::Error;

/// Errors that can occur during SQL parsing
#[derive(Error, Debug)]
pub enum ParserError {
    #[error("SQL parsing error: {0}")]
    ParseError(String),
    
    #[error("Unsupported SQL feature: {0}")]
    UnsupportedFeature(String),
    
    #[error("Invalid query structure: {0}")]
    InvalidStructure(String),
}

impl From<sqlparser::parser::ParserError> for ParserError {
    fn from(err: sqlparser::parser::ParserError) -> Self {
        ParserError::ParseError(err.to_string())
    }
}

/// Result type for parsing operations
pub type Result<T> = std::result::Result<T, ParserError>;

/// Parsed SQL result
#[derive(Debug, Clone)]
pub struct ParseResult {
    /// Abstract syntax tree node
    pub ast: ASTNode,
    /// Original SQL string
    #[allow(dead_code)]
    pub sql: String,
}

/// Abstract syntax tree node representing parsed SQL
#[derive(Debug, Clone)]
pub enum ASTNode {
    /// SELECT query
    Select(SelectNode),
    /// INSERT statement
    Insert(InsertNode),
    /// UPDATE statement
    Update(UpdateNode),
    /// DELETE statement
    Delete(DeleteNode),
    /// CREATE TABLE
    CreateTable(CreateTableNode),
    /// DROP TABLE
    DropTable(DropTableNode),
}

/// SELECT query node
#[derive(Debug, Clone)]
pub struct SelectNode {
    /// Columns to select
    pub columns: Vec<SelectItem>,
    /// Table to select from
    pub from: Option<String>,
    /// WHERE clause
    pub where_clause: Option<Expr>,
    /// JOIN clauses
    pub joins: Vec<JoinNode>,
    /// GROUP BY columns
    pub group_by: Vec<Expr>,
    /// HAVING clause
    pub having: Option<Expr>,
    /// ORDER BY columns
    pub order_by: Vec<OrderByNode>,
    /// LIMIT clause
    pub limit: Option<u64>,
}

/// JOIN clause node
#[derive(Debug, Clone)]
pub struct JoinNode {
    /// Table to join
    pub table: String,
    /// Join type
    pub join_type: JoinType,
    /// Join condition
    pub condition: Option<Expr>,
}

/// Join types
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
#[allow(dead_code)]
pub enum JoinType {
    Inner,
    Left,
    Right,
    Full,
}

/// ORDER BY node
#[derive(Debug, Clone)]
pub struct OrderByNode {
    /// Expression to order by
    pub expr: Expr,
    /// Ascending or descending
    #[allow(dead_code)]
    pub ascending: bool,
}

/// INSERT statement node
#[derive(Debug, Clone)]
pub struct InsertNode {
    /// Table to insert into
    pub table: String,
    /// Column names
    #[allow(dead_code)]
    pub columns: Vec<String>,
    /// Values to insert
    #[allow(dead_code)]
    pub values: Vec<Vec<Expr>>,
}

/// UPDATE statement node
#[derive(Debug, Clone)]
pub struct UpdateNode {
    /// Table to update
    pub table: String,
    /// Column assignments
    #[allow(dead_code)]
    pub assignments: Vec<(String, Expr)>,
    /// WHERE clause
    pub where_clause: Option<Expr>,
}

/// DELETE statement node
#[derive(Debug, Clone)]
pub struct DeleteNode {
    /// Table to delete from
    pub table: String,
    /// WHERE clause
    pub where_clause: Option<Expr>,
}

/// CREATE TABLE node
#[derive(Debug, Clone)]
pub struct CreateTableNode {
    /// Table name
    pub table: String,
    /// Column definitions
    pub columns: Vec<ColumnDef>,
    /// Primary key
    #[allow(dead_code)]
    pub primary_key: Vec<String>,
    /// Foreign keys
    #[allow(dead_code)]
    pub foreign_keys: Vec<ForeignKeyDef>,
}

/// Column definition
#[derive(Debug, Clone)]
pub struct ColumnDef {
    /// Column name
    pub name: String,
    /// Data type
    pub data_type: String,
    /// Whether nullable
    pub nullable: bool,
    /// Default value
    #[allow(dead_code)]
    pub default: Option<Expr>,
}

/// Foreign key definition
#[derive(Debug, Clone)]
pub struct ForeignKeyDef {
    /// Local columns
    #[allow(dead_code)]
    pub columns: Vec<String>,
    /// Referenced table
    #[allow(dead_code)]
    pub ref_table: String,
    /// Referenced columns
    #[allow(dead_code)]
    pub ref_columns: Vec<String>,
}

/// DROP TABLE node
#[derive(Debug, Clone)]
pub struct DropTableNode {
    /// Table name
    pub table: String,
    /// Whether to check if table exists
    #[allow(dead_code)]
    pub if_exists: bool,
}

/// SQL Parser - parses SQL strings into AST
pub struct SQLParser;

impl SQLParser {
    /// Parse a SQL string into an AST
    pub fn parse(sql: &str) -> Result<ParseResult> {
        let dialect = GenericDialect {};
        let statements = Parser::new(&dialect).try_with_sql(sql)
            .map_err(|e| ParserError::ParseError(format!("Parser initialization error: {}", e)))?
            .parse_statements()?;
        
        if statements.is_empty() {
            return Err(ParserError::ParseError("No statements found".to_string()));
        }
        
        if statements.len() > 1 {
            return Err(ParserError::ParseError("Multiple statements not supported".to_string()));
        }
        
        let statement = statements.into_iter().next().unwrap();
        let ast = Self::statement_to_ast(statement)?;
        
        Ok(ParseResult {
            ast,
            sql: sql.to_string(),
        })
    }
    
    /// Convert sqlparser AST to our AST
    fn statement_to_ast(statement: Statement) -> Result<ASTNode> {
        match statement {
            Statement::Query(query) => Self::query_to_ast(*query),
            Statement::Insert { table_name, columns, source, .. } => {
                let values = if let Some(query) = source {
                    Self::extract_values_from_query(*query)?
                } else {
                    Vec::new()
                };
                Ok(ASTNode::Insert(InsertNode {
                    table: table_name.to_string(),
                    columns: columns.iter().map(|c| c.to_string()).collect(),
                    values,
                }))
            }
            Statement::Update { table, assignments, selection, .. } => {
                let where_clause = selection;
                let mut ast_assignments = Vec::new();
                
                for assignment in assignments {
                    let col = assignment.id[0].to_string();
                    let expr = assignment.value;
                    ast_assignments.push((col, expr));
                }
                
                Ok(ASTNode::Update(UpdateNode {
                    table: table.to_string(),
                    assignments: ast_assignments,
                    where_clause,
                }))
            }
            Statement::Delete { from, selection, .. } => {
                let table_name = from[0].to_string();
                Ok(ASTNode::Delete(DeleteNode {
                    table: table_name,
                    where_clause: selection,
                }))
            }
            Statement::CreateTable { name, columns, .. } => {
                let mut ast_columns = Vec::new();
                let mut primary_key = Vec::new();
                let foreign_keys = Vec::new();
                
                for column in columns {
                    let col_name = column.name.to_string();
                    let data_type = Self::data_type_to_string(&column.data_type);
                    let nullable = !column.options.iter().any(|opt| {
                        matches!(opt.option, sqlparser::ast::ColumnOption::NotNull { .. })
                    });
                    
                    ast_columns.push(ColumnDef {
                        name: col_name.clone(),
                        data_type,
                        nullable,
                        default: None,
                    });
                    
                    // Check for primary key constraint
                    for opt in &column.options {
                        if matches!(opt.option, sqlparser::ast::ColumnOption::Unique { is_primary: true, .. }) {
                            primary_key.push(col_name.clone());
                        }
                    }
                }
                
                Ok(ASTNode::CreateTable(CreateTableNode {
                    table: name.to_string(),
                    columns: ast_columns,
                    primary_key,
                    foreign_keys,
                }))
            }
            Statement::Drop { names, if_exists, .. } => {
                let table_name = names[0].to_string();
                Ok(ASTNode::DropTable(DropTableNode {
                    table: table_name,
                    if_exists,
                }))
            }
            _ => Err(ParserError::UnsupportedFeature(format!("{:?}", statement))),
        }
    }
    
    /// Convert a query to AST
    fn query_to_ast(query: Query) -> Result<ASTNode> {
        let body = query.body;
        let select_node = Self::set_expr_to_select(*body)?;
        
        Ok(ASTNode::Select(select_node))
    }
    
    /// Convert SetExpr to SelectNode
    fn set_expr_to_select(set_expr: SetExpr) -> Result<SelectNode> {
        match set_expr {
            SetExpr::Select(select) => Self::select_to_node(*select),
            _ => Err(ParserError::UnsupportedFeature("Only SELECT statements are supported".to_string())),
        }
    }
    
    /// Convert sqlparser Select to our SelectNode
    fn select_to_node(select: Select) -> Result<SelectNode> {
        let from = select.from.iter().next().map(|f| {
            f.relation.to_string()
        });
        
        // Simplified - ignore joins, group_by, having, order_by, limit for now
        let joins = Vec::new();
        
        Ok(SelectNode {
            columns: select.projection,
            from,
            where_clause: select.selection,
            joins,
            group_by: Vec::new(), // Simplified
            having: None,
            order_by: Vec::new(), // Simplified
            limit: None, // Simplified
        })
    }
    
    /// Extract values from a query (simplified)
    fn extract_values_from_query(_query: Query) -> Result<Vec<Vec<Expr>>> {
        // In a real implementation, this would parse the VALUES clause
        Ok(Vec::new())
    }
    
    /// Convert sqlparser data type to string
    fn data_type_to_string(data_type: &sqlparser::ast::DataType) -> String {
        match data_type {
            sqlparser::ast::DataType::Varchar(_) => "VARCHAR".to_string(),
            sqlparser::ast::DataType::Int(_) => "INT".to_string(),
            sqlparser::ast::DataType::Float(_) => "FLOAT".to_string(),
            sqlparser::ast::DataType::Boolean => "BOOLEAN".to_string(),
            sqlparser::ast::DataType::Text => "TEXT".to_string(),
            _ => "VARCHAR".to_string(), // Default
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_simple_select() {
        let sql = "SELECT * FROM users";
        let result = SQLParser::parse(sql);
        assert!(result.is_ok());
    }

    #[test]
    fn test_create_table() {
        let sql = "CREATE TABLE users (id INT, name VARCHAR(255))";
        let result = SQLParser::parse(sql);
        assert!(result.is_ok());
    }
}
