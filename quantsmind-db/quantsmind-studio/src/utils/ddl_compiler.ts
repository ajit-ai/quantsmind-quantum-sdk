// DDL Compiler - Compiles canvas nodes and edges into ANSI SQL DDL

import { TableNode, Edge, ColumnDefinition } from '../types/schema';

/**
 * Compile canvas nodes and edges into ANSI PostgreSQL DDL statements
 */
export function compileDDL(nodes: TableNode[], edges: Edge[]): string {
  const statements: string[] = [];

  // First, compile CREATE TABLE statements
  for (const node of nodes) {
    statements.push(compileCreateTable(node));
  }

  // Then, compile ALTER TABLE statements for foreign keys
  for (const edge of edges) {
    const fkStatement = compileForeignKey(edge, nodes);
    if (fkStatement) {
      statements.push(fkStatement);
    }
  }

  return statements.join('\n\n');
}

/**
 * Compile a single table node into a CREATE TABLE statement
 */
function compileCreateTable(node: TableNode): string {
  const { tableName, columns } = node.data;
  const columnDefs: string[] = [];
  const primaryKeyColumns: string[] = [];

  for (const column of columns) {
    const columnDef = compileColumnDefinition(column);
    columnDefs.push(columnDef);

    if (column.primaryKey) {
      primaryKeyColumns.push(column.name);
    }
  }

  // Add primary key constraint if there are primary key columns
  if (primaryKeyColumns.length > 0) {
    columnDefs.push(`PRIMARY KEY (${primaryKeyColumns.join(', ')})`);
  }

  return `CREATE TABLE ${tableName} (\n  ${columnDefs.join(',\n  ')}\n);`;
}

/**
 * Compile a column definition into SQL
 */
function compileColumnDefinition(column: ColumnDefinition): string {
  let def = `${column.name} ${column.dataType}`;

  if (!column.nullable) {
    def += ' NOT NULL';
  }

  return def;
}

/**
 * Compile an edge into a foreign key constraint
 */
function compileForeignKey(edge: Edge, nodes: TableNode[]): string | null {
  const sourceNode = nodes.find(n => n.id === edge.source);
  const targetNode = nodes.find(n => n.id === edge.target);

  if (!sourceNode || !targetNode) {
    return null;
  }

  // Extract column names from handles (format: "table-column")
  const sourceColumn = edge.sourceHandle?.split('-')[1] || '';
  const targetColumn = edge.targetHandle?.split('-')[1] || '';

  if (!sourceColumn || !targetColumn) {
    return null;
  }

  const constraintName = `fk_${sourceNode.data.tableName}_${sourceColumn}`;
  
  return `ALTER TABLE ${sourceNode.data.tableName}\n  ADD CONSTRAINT ${constraintName}\n  FOREIGN KEY (${sourceColumn})\n  REFERENCES ${targetNode.data.tableName}(${targetColumn});`;
}

/**
 * Format DDL with proper indentation
 */
export function formatDDL(ddl: string): string {
  return ddl
    .replace(/\n\s*\n/g, '\n\n') // Remove excessive blank lines
    .replace(/^\s+|\s+$/g, '') // Trim leading/trailing whitespace
    .trim();
}

/**
 * Validate canvas state before compilation
 */
export function validateCanvas(nodes: TableNode[], edges: Edge[]): { valid: boolean; errors: string[] } {
  const errors: string[] = [];

  // Check that all tables have at least one column
  for (const node of nodes) {
    if (node.data.columns.length === 0) {
      errors.push(`Table "${node.data.tableName}" has no columns`);
    }

    // Check that all columns have names
    for (const column of node.data.columns) {
      if (!column.name.trim()) {
        errors.push(`Table "${node.data.tableName}" has a column with no name`);
      }
    }

    // Check that table names are unique
    const duplicateTables = nodes.filter(n => n.data.tableName === node.data.tableName);
    if (duplicateTables.length > 1) {
      errors.push(`Duplicate table name: "${node.data.tableName}"`);
    }
  }

  // Check that all edges connect to valid nodes
  for (const edge of edges) {
    const sourceExists = nodes.some(n => n.id === edge.source);
    const targetExists = nodes.some(n => n.id === edge.target);

    if (!sourceExists) {
      errors.push(`Edge references non-existent source node: ${edge.source}`);
    }

    if (!targetExists) {
      errors.push(`Edge references non-existent target node: ${edge.target}`);
    }
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}

/**
 * Generate the default QuantsMind schema as canvas state
 */
export function generateDefaultSchema(): { nodes: TableNode[]; edges: Edge[] } {
  const nodes: TableNode[] = [
    {
      id: 'users',
      type: 'table',
      position: { x: 100, y: 100 },
      data: {
        tableName: 'users',
        columns: [
          { name: 'user_id', dataType: 'UUID', nullable: false, primaryKey: true },
          { name: 'email', dataType: 'VARCHAR(255)', nullable: false, primaryKey: false },
          { name: 'organization', dataType: 'VARCHAR(100)', nullable: false, primaryKey: false },
          { name: 'created_at', dataType: 'TIMESTAMP', nullable: false, primaryKey: false },
        ],
      },
    },
    {
      id: 'api_keys',
      type: 'table',
      position: { x: 500, y: 100 },
      data: {
        tableName: 'api_keys',
        columns: [
          { name: 'key_id', dataType: 'UUID', nullable: false, primaryKey: true },
          { name: 'user_id', dataType: 'UUID', nullable: false, primaryKey: false },
          { name: 'key_hash', dataType: 'VARCHAR(64)', nullable: false, primaryKey: false },
          { name: 'rate_limit_rpm', dataType: 'INT', nullable: false, primaryKey: false },
        ],
      },
    },
    {
      id: 'compute_jobs',
      type: 'table',
      position: { x: 100, y: 400 },
      data: {
        tableName: 'compute_jobs',
        columns: [
          { name: 'job_id', dataType: 'UUID', nullable: false, primaryKey: true },
          { name: 'user_id', dataType: 'UUID', nullable: false, primaryKey: false },
          { name: 'target_backend', dataType: 'VARCHAR(50)', nullable: false, primaryKey: false },
          { name: 'status', dataType: 'VARCHAR(20)', nullable: false, primaryKey: false },
          { name: 'execution_time_ms', dataType: 'INT', nullable: true, primaryKey: false },
          { name: 'created_at', dataType: 'TIMESTAMP', nullable: false, primaryKey: false },
        ],
      },
    },
    {
      id: 'risk_evaluations',
      type: 'table',
      position: { x: 500, y: 400 },
      data: {
        tableName: 'risk_evaluations',
        columns: [
          { name: 'eval_id', dataType: 'UUID', nullable: false, primaryKey: true },
          { name: 'job_id', dataType: 'UUID', nullable: false, primaryKey: false },
          { name: 'portfolio_id', dataType: 'UUID', nullable: false, primaryKey: false },
          { name: 'var_99', dataType: 'NUMERIC(20,6)', nullable: false, primaryKey: false },
          { name: 'sharpe_ratio', dataType: 'NUMERIC(10,4)', nullable: false, primaryKey: false },
          { name: 'max_drawdown', dataType: 'NUMERIC(20,6)', nullable: false, primaryKey: false },
          { name: 'evaluated_at', dataType: 'TIMESTAMP', nullable: false, primaryKey: false },
        ],
      },
    },
  ];

  const edges: Edge[] = [
    {
      id: 'fk_api_keys_user_id',
      source: 'api_keys',
      target: 'users',
      sourceHandle: 'api_keys-user_id',
      targetHandle: 'users-user_id',
      data: { relationship: 'fk_api_keys_user_id' },
    },
    {
      id: 'fk_compute_jobs_user_id',
      source: 'compute_jobs',
      target: 'users',
      sourceHandle: 'compute_jobs-user_id',
      targetHandle: 'users-user_id',
      data: { relationship: 'fk_compute_jobs_user_id' },
    },
    {
      id: 'fk_risk_evaluations_job_id',
      source: 'risk_evaluations',
      target: 'compute_jobs',
      sourceHandle: 'risk_evaluations-job_id',
      targetHandle: 'compute_jobs-job_id',
      data: { relationship: 'fk_risk_evaluations_job_id' },
    },
  ];

  return { nodes, edges };
}
