// Type definitions for QuantsMind Studio schema and canvas

export interface ColumnDefinition {
  name: string;
  dataType: string;
  nullable: boolean;
  primaryKey: boolean;
}

export interface TableNode {
  id: string;
  type: 'table';
  position: { x: number; y: number };
  data: {
    tableName: string;
    columns: ColumnDefinition[];
  };
}

export interface Edge {
  id: string;
  source: string;
  target: string;
  sourceHandle?: string;
  targetHandle?: string;
  data: {
    relationship: string;
  };
}

export interface CanvasState {
  nodes: TableNode[];
  edges: Edge[];
}

export const DATA_TYPES = [
  'UUID',
  'VARCHAR',
  'INT',
  'NUMERIC',
  'BOOLEAN',
  'TIMESTAMP',
] as const;

export type DataType = typeof DATA_TYPES[number];
