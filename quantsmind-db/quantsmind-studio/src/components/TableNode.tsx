// Custom Table Node component for React Flow
// Displays a database table with columns, data types, and primary key indicators

import React, { useCallback } from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import { Key, Plus, X } from 'lucide-react';
import { ColumnDefinition, DATA_TYPES } from '../types/schema';

interface TableNodeData {
  tableName: string;
  columns: ColumnDefinition[];
  onTableNameChange?: (tableName: string) => void;
  onColumnChange?: (index: number, column: ColumnDefinition) => void;
  onColumnAdd?: () => void;
  onColumnRemove?: (index: number) => void;
}

export default function TableNode({ data, selected }: NodeProps<TableNodeData>) {
  const nodeData = data as TableNodeData;

  const handleTableNameChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (nodeData.onTableNameChange) {
      nodeData.onTableNameChange(e.target.value);
    }
  }, [nodeData]);

  const handleColumnChange = useCallback((index: number, field: keyof ColumnDefinition, value: any) => {
    if (nodeData.onColumnChange) {
      const updatedColumn = { ...nodeData.columns[index], [field]: value };
      nodeData.onColumnChange(index, updatedColumn);
    }
  }, [nodeData]);

  const handleAddColumn = useCallback(() => {
    if (nodeData.onColumnAdd) {
      nodeData.onColumnAdd();
    }
  }, [nodeData]);

  const handleRemoveColumn = useCallback((index: number) => {
    if (nodeData.onColumnRemove) {
      nodeData.onColumnRemove(index);
    }
  }, [nodeData]);

  return (
    <div
      className={`table-node ${selected ? 'selected' : ''}`}
      style={{
        background: '#1e1e1e',
        border: `2px solid ${selected ? '#3b82f6' : '#4a4a4a'}`,
        borderRadius: '8px',
        minWidth: '300px',
        maxWidth: '400px',
        fontFamily: 'monospace',
        fontSize: '12px',
        color: '#e0e0e0',
        boxShadow: selected ? '0 0 10px rgba(59, 130, 246, 0.5)' : '0 2px 4px rgba(0,0,0,0.3)',
      }}
    >
      {/* Left handle for foreign key targeting */}
      <Handle
        type="target"
        position={Position.Left}
        style={{ background: '#4a4a4a', width: 8, height: 8 }}
        isConnectable={true}
      />

      {/* Table header */}
      <div
        style={{
          padding: '12px',
          borderBottom: '1px solid #4a4a4a',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          background: '#2d2d2d',
          borderTopLeftRadius: '6px',
          borderTopRightRadius: '6px',
        }}
      >
        <input
          type="text"
          value={nodeData.tableName}
          onChange={handleTableNameChange}
          style={{
            background: 'transparent',
            border: 'none',
            color: '#3b82f6',
            fontSize: '14px',
            fontWeight: 'bold',
            fontFamily: 'monospace',
            width: '70%',
            outline: 'none',
          }}
        />
        <button
          onClick={handleAddColumn}
          style={{
            background: '#3b82f6',
            border: 'none',
            borderRadius: '4px',
            padding: '4px 8px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            color: 'white',
            fontSize: '10px',
          }}
          title="Add Column"
        >
          <Plus size={12} />
        </button>
      </div>

      {/* Columns */}
      <div style={{ padding: '8px' }}>
        {nodeData.columns.map((column, index) => (
          <div
            key={index}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '6px',
              borderBottom: index < nodeData.columns.length - 1 ? '1px solid #3a3a3a' : 'none',
              position: 'relative',
            }}
          >
            {/* Primary Key Toggle */}
            <button
              onClick={() => handleColumnChange(index, 'primaryKey', !column.primaryKey)}
              style={{
                background: column.primaryKey ? '#f59e0b' : '#3a3a3a',
                border: 'none',
                borderRadius: '4px',
                padding: '4px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                color: 'white',
              }}
              title={column.primaryKey ? 'Primary Key' : 'Set as Primary Key'}
            >
              <Key size={12} />
            </button>

            {/* Column Name */}
            <input
              type="text"
              value={column.name}
              onChange={(e) => handleColumnChange(index, 'name', e.target.value)}
              placeholder="column_name"
              style={{
                flex: 1,
                background: '#2d2d2d',
                border: '1px solid #4a4a4a',
                borderRadius: '4px',
                padding: '4px 8px',
                color: '#e0e0e0',
                fontSize: '11px',
                fontFamily: 'monospace',
                outline: 'none',
              }}
            />

            {/* Data Type Selector */}
            <select
              value={column.dataType}
              onChange={(e) => handleColumnChange(index, 'dataType', e.target.value)}
              style={{
                background: '#2d2d2d',
                border: '1px solid #4a4a4a',
                borderRadius: '4px',
                padding: '4px',
                color: '#e0e0e0',
                fontSize: '10px',
                fontFamily: 'monospace',
                outline: 'none',
                cursor: 'pointer',
              }}
            >
              {DATA_TYPES.map((type) => (
                <option key={type} value={type}>
                  {type}
                </option>
              ))}
            </select>

            {/* Nullable Toggle */}
            <label
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                fontSize: '10px',
                cursor: 'pointer',
                color: column.nullable ? '#9ca3af' : '#e0e0e0',
              }}
            >
              <input
                type="checkbox"
                checked={column.nullable}
                onChange={(e) => handleColumnChange(index, 'nullable', e.target.checked)}
                style={{ cursor: 'pointer' }}
              />
              NULL
            </label>

            {/* Remove Column Button */}
            <button
              onClick={() => handleRemoveColumn(index)}
              style={{
                background: '#ef4444',
                border: 'none',
                borderRadius: '4px',
                padding: '4px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                color: 'white',
              }}
              title="Remove Column"
            >
              <X size={12} />
            </button>

            {/* Right handle for this column */}
            <Handle
              type="source"
              position={Position.Right}
              id={`${nodeData.tableName}-${column.name}`}
              style={{
                background: '#4a4a4a',
                width: 8,
                height: 8,
                position: 'absolute',
                right: -4,
                top: '50%',
                transform: 'translateY(-50%)',
              }}
              isConnectable={true}
            />
          </div>
        ))}

        {nodeData.columns.length === 0 && (
          <div
            style={{
              padding: '20px',
              textAlign: 'center',
              color: '#6b7280',
              fontSize: '11px',
            }}
          >
            No columns. Click + to add one.
          </div>
        )}
      </div>

      {/* Right handle for table-level connections */}
      <Handle
        type="source"
        position={Position.Right}
        style={{ background: '#4a4a4a', width: 8, height: 8 }}
        isConnectable={true}
      />
    </div>
  );
}
