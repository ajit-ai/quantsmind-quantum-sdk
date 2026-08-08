// Canvas component - React Flow diagram with table nodes and DDL generation

import React, { useCallback, useMemo, useState } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  addEdge,
  Connection,
  Edge,
  Node,
  useNodesState,
  useEdgesState,
  OnConnect,
} from 'reactflow';
import 'reactflow/dist/style.css';
import TableNode from './TableNode';
import { compileDDL, validateCanvas, generateDefaultSchema } from '../utils/ddl_compiler';
import { TableNode as TableNodeType, ColumnDefinition } from '../types/schema';
import { Plus, Download, Copy, CheckCircle, AlertCircle } from 'lucide-react';

const nodeTypes = {
  table: TableNode,
};

export default function Canvas() {
  // Initialize with default QuantsMind schema
  const { nodes: initialNodes, edges: initialEdges } = generateDefaultSchema();
  
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [showDDL, setShowDDL] = useState(false);
  const [ddlCopied, setDdlCopied] = useState(false);

  // Handle new connections
  const onConnect: OnConnect = useCallback(
    (connection: Connection) => {
      setEdges((eds) => addEdge(connection, eds));
    },
    [setEdges]
  );

  // Add a new table node
  const addTable = useCallback(() => {
    const newId = `table_${Date.now()}`;
    const newNode: Node = {
      id: newId,
      type: 'table',
      position: { x: Math.random() * 500 + 100, y: Math.random() * 500 + 100 },
      data: {
        tableName: `new_table_${nodes.length + 1}`,
        columns: [
          { name: 'id', dataType: 'UUID', nullable: false, primaryKey: true },
        ],
        onTableNameChange: (tableName: string) => updateTableName(newId, tableName),
        onColumnChange: (index: number, column: ColumnDefinition) => updateColumn(newId, index, column),
        onColumnAdd: () => addColumn(newId),
        onColumnRemove: (index: number) => removeColumn(newId, index),
      },
    };
    setNodes((nds) => [...nds, newNode]);
  }, [nodes.length, setNodes]);

  // Update table name
  const updateTableName = useCallback((nodeId: string, tableName: string) => {
    setNodes((nds) =>
      nds.map((node) =>
        node.id === nodeId
          ? { ...node, data: { ...node.data, tableName } }
          : node
      )
    );
  }, [setNodes]);

  // Update column
  const updateColumn = useCallback((nodeId: string, index: number, column: ColumnDefinition) => {
    setNodes((nds) =>
      nds.map((node) => {
        if (node.id === nodeId) {
          const updatedColumns = [...node.data.columns];
          updatedColumns[index] = column;
          return { ...node, data: { ...node.data, columns: updatedColumns } };
        }
        return node;
      })
    );
  }, [setNodes]);

  // Add column to table
  const addColumn = useCallback((nodeId: string) => {
    setNodes((nds) =>
      nds.map((node) => {
        if (node.id === nodeId) {
          const newColumn: ColumnDefinition = {
            name: `column_${node.data.columns.length + 1}`,
            dataType: 'VARCHAR(255)',
            nullable: true,
            primaryKey: false,
          };
          return {
            ...node,
            data: { ...node.data, columns: [...node.data.columns, newColumn] },
          };
        }
        return node;
      })
    );
  }, [setNodes]);

  // Remove column from table
  const removeColumn = useCallback((nodeId: string, index: number) => {
    setNodes((nds) =>
      nds.map((node) => {
        if (node.id === nodeId) {
          const updatedColumns = node.data.columns.filter((_, i) => i !== index);
          return { ...node, data: { ...node.data, columns: updatedColumns } };
        }
        return node;
      })
    );
  }, [setNodes]);

  // Compile DDL from current canvas state
  const ddl = useMemo(() => {
    const tableNodes = nodes.filter((node): node is TableNodeType => node.type === 'table');
    return compileDDL(tableNodes, edges);
  }, [nodes, edges]);

  // Validate canvas
  const validation = useMemo(() => {
    const tableNodes = nodes.filter((node): node is TableNodeType => node.type === 'table');
    return validateCanvas(tableNodes, edges);
  }, [nodes, edges]);

  // Copy DDL to clipboard
  const copyDDL = useCallback(() => {
    navigator.clipboard.writeText(ddl);
    setDdlCopied(true);
    setTimeout(() => setDdlCopied(false), 2000);
  }, [ddl]);

  // Download DDL as file
  const downloadDDL = useCallback(() => {
    const blob = new Blob([ddl], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'quantsmind_schema.sql';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, [ddl]);

  return (
    <div style={{ width: '100%', height: '100%', display: 'flex' }}>
      {/* Main Canvas Area */}
      <div style={{ flex: 1, position: 'relative' }}>
        {/* Toolbar */}
        <div
          style={{
            position: 'absolute',
            top: '16px',
            left: '16px',
            zIndex: 10,
            display: 'flex',
            gap: '8px',
          }}
        >
          <button
            onClick={addTable}
            style={{
              background: '#3b82f6',
              border: 'none',
              borderRadius: '6px',
              padding: '8px 16px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              color: 'white',
              fontSize: '14px',
              fontWeight: '500',
              boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
            }}
          >
            <Plus size={16} />
            Add Table
          </button>

          <button
            onClick={() => setShowDDL(!showDDL)}
            style={{
              background: showDDL ? '#10b981' : '#4a4a4a',
              border: 'none',
              borderRadius: '6px',
              padding: '8px 16px',
              cursor: 'pointer',
              color: 'white',
              fontSize: '14px',
              fontWeight: '500',
              boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
            }}
          >
            {showDDL ? 'Hide DDL' : 'Show DDL'}
          </button>
        </div>

        {/* Validation Status */}
        <div
          style={{
            position: 'absolute',
            top: '16px',
            right: showDDL ? '416px' : '16px',
            zIndex: 10,
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '8px 12px',
            borderRadius: '6px',
            background: validation.valid ? '#065f46' : '#7f1d1d',
            color: 'white',
            fontSize: '12px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
          }}
        >
          {validation.valid ? (
            <>
              <CheckCircle size={14} />
              Schema Valid
            </>
          ) : (
            <>
              <AlertCircle size={14} />
              {validation.errors.length} Error(s)
            </>
          )}
        </div>

        {/* React Flow Canvas */}
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          nodeTypes={nodeTypes}
          fitView
          style={{ background: '#1a1a1a' }}
        >
          <Background color="#2a2a2a" gap={16} />
          <Controls style={{ background: '#2d2d2d', fill: '#e0e0e0' }} />
          <MiniMap
            style={{
              background: '#2d2d2d',
              fill: '#3b82f6',
              stroke: '#4a4a4a',
            }}
            nodeColor="#3b82f6"
            maskColor="rgba(0, 0, 0, 0.6)"
          />
        </ReactFlow>
      </div>

      {/* DDL Drawer */}
      {showDDL && (
        <div
          style={{
            width: '400px',
            background: '#1e1e1e',
            borderLeft: '1px solid #4a4a4a',
            display: 'flex',
            flexDirection: 'column',
            height: '100%',
          }}
        >
          {/* DDL Header */}
          <div
            style={{
              padding: '16px',
              borderBottom: '1px solid #4a4a4a',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            <h3 style={{ margin: 0, color: '#e0e0e0', fontSize: '16px' }}>
              Generated DDL
            </h3>
            <div style={{ display: 'flex', gap: '8px' }}>
              <button
                onClick={copyDDL}
                style={{
                  background: ddlCopied ? '#10b981' : '#3b82f6',
                  border: 'none',
                  borderRadius: '4px',
                  padding: '6px 12px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  color: 'white',
                  fontSize: '12px',
                }}
              >
                {ddlCopied ? <CheckCircle size={14} /> : <Copy size={14} />}
                {ddlCopied ? 'Copied!' : 'Copy'}
              </button>
              <button
                onClick={downloadDDL}
                style={{
                  background: '#4a4a4a',
                  border: 'none',
                  borderRadius: '4px',
                  padding: '6px 12px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  color: 'white',
                  fontSize: '12px',
                }}
              >
                <Download size={14} />
                Export
              </button>
            </div>
          </div>

          {/* DDL Content */}
          <div
            style={{
              flex: 1,
              padding: '16px',
              overflow: 'auto',
            }}
          >
            <pre
              style={{
                margin: 0,
                fontFamily: 'monospace',
                fontSize: '12px',
                color: '#e0e0e0',
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-word',
              }}
            >
              {ddl}
            </pre>
          </div>

          {/* Validation Errors */}
          {!validation.valid && (
            <div
              style={{
                padding: '16px',
                borderTop: '1px solid #4a4a4a',
                background: '#2d1f1f',
              }}
            >
              <h4 style={{ margin: '0 0 8px 0', color: '#ef4444', fontSize: '14px' }}>
                Validation Errors
              </h4>
              <ul
                style={{
                  margin: 0,
                  paddingLeft: '20px',
                  color: '#fca5a5',
                  fontSize: '12px',
                }}
              >
                {validation.errors.map((error, index) => (
                  <li key={index}>{error}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
