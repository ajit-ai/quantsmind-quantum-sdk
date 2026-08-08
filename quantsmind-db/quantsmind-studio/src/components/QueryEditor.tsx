// Query Editor component - Monaco editor with SQL syntax highlighting

import React, { useState, useCallback } from 'react';
import Editor from '@monaco-editor/react';
import { Play, Database, AlertCircle, CheckCircle } from 'lucide-react';

interface QueryEditorProps {
  onExecute: (sql: string) => Promise<{ success: boolean; message: string; rows: string[][]; columns: string[]; executionTimeMs: number }>;
  isConnected: boolean;
}

export default function QueryEditor({ onExecute, isConnected }: QueryEditorProps) {
  const [sql, setSql] = useState('SELECT * FROM users LIMIT 10;');
  const [isExecuting, setIsExecuting] = useState(false);
  const [result, setResult] = useState<{
    success: boolean;
    message: string;
    rows: string[][];
    columns: string[];
    executionTimeMs: number;
  } | null>(null);

  const handleExecute = useCallback(async () => {
    if (!isConnected) {
      setResult({
        success: false,
        message: 'Not connected to database',
        rows: [],
        columns: [],
        executionTimeMs: 0,
      });
      return;
    }

    setIsExecuting(true);
    try {
      const response = await onExecute(sql);
      setResult(response);
    } catch (error) {
      setResult({
        success: false,
        message: error instanceof Error ? error.message : 'Unknown error',
        rows: [],
        columns: [],
        executionTimeMs: 0,
      });
    } finally {
      setIsExecuting(false);
    }
  }, [sql, isConnected, onExecute]);

  const handleEditorChange = useCallback((value: string | undefined) => {
    setSql(value || '');
  }, []);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    // Execute on Ctrl+Enter or Cmd+Enter
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      handleExecute();
    }
  }, [handleExecute]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', background: '#1e1e1e' }}>
      {/* Editor Header */}
      <div
        style={{
          padding: '12px 16px',
          borderBottom: '1px solid #4a4a4a',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          background: '#2d2d2d',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Database size={18} style={{ color: '#3b82f6' }} />
          <span style={{ color: '#e0e0e0', fontSize: '14px', fontWeight: '500' }}>
            SQL Query Editor
          </span>
          <span
            style={{
              fontSize: '11px',
              padding: '2px 8px',
              borderRadius: '4px',
              background: isConnected ? '#065f46' : '#7f1d1d',
              color: 'white',
            }}
          >
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>

        <button
          onClick={handleExecute}
          disabled={isExecuting || !isConnected}
          style={{
            background: isExecuting ? '#4a4a4a' : '#3b82f6',
            border: 'none',
            borderRadius: '6px',
            padding: '8px 16px',
            cursor: isExecuting || !isConnected ? 'not-allowed' : 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            color: 'white',
            fontSize: '13px',
            fontWeight: '500',
            opacity: isExecuting || !isConnected ? 0.5 : 1,
          }}
        >
          <Play size={14} />
          {isExecuting ? 'Executing...' : 'Run (Ctrl+Enter)'}
        </button>
      </div>

      {/* Monaco Editor */}
      <div style={{ flex: 1, minHeight: '200px' }}>
        <Editor
          height="100%"
          defaultLanguage="sql"
          value={sql}
          onChange={handleEditorChange}
          theme="vs-dark"
          options={{
            minimap: { enabled: false },
            fontSize: 13,
            lineNumbers: 'on',
            scrollBeyondLastLine: false,
            automaticLayout: true,
            tabSize: 2,
            wordWrap: 'on',
            padding: { top: 16, bottom: 16 },
          }}
          onKeyDown={handleKeyDown}
        />
      </div>

      {/* Query Result */}
      {result && (
        <div
          style={{
            borderTop: '1px solid #4a4a4a',
            background: '#1a1a1a',
            maxHeight: '50%',
            overflow: 'auto',
          }}
        >
          {/* Result Header */}
          <div
            style={{
              padding: '12px 16px',
              borderBottom: '1px solid #3a3a3a',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              {result.success ? (
                <CheckCircle size={16} style={{ color: '#10b981' }} />
              ) : (
                <AlertCircle size={16} style={{ color: '#ef4444' }} />
              )}
              <span style={{ color: '#e0e0e0', fontSize: '13px' }}>
                {result.message}
              </span>
            </div>
            <span style={{ color: '#9ca3af', fontSize: '11px' }}>
              {result.executionTimeMs}ms
            </span>
          </div>

          {/* Result Table */}
          {result.success && result.rows.length > 0 && (
            <div style={{ overflow: 'auto' }}>
              <table
                style={{
                  width: '100%',
                  borderCollapse: 'collapse',
                  fontSize: '12px',
                  fontFamily: 'monospace',
                }}
              >
                <thead>
                  <tr style={{ background: '#2d2d2d', position: 'sticky', top: 0 }}>
                    {result.columns.map((column, index) => (
                      <th
                        key={index}
                        style={{
                          padding: '8px 12px',
                          textAlign: 'left',
                          borderBottom: '1px solid #4a4a4a',
                          color: '#e0e0e0',
                          fontWeight: '500',
                          whiteSpace: 'nowrap',
                        }}
                      >
                        {column}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {result.rows.map((row, rowIndex) => (
                    <tr
                      key={rowIndex}
                      style={{
                        borderBottom: '1px solid #3a3a3a',
                        background: rowIndex % 2 === 0 ? '#1e1e1e' : '#252525',
                      }}
                    >
                      {row.map((cell, cellIndex) => (
                        <td
                          key={cellIndex}
                          style={{
                            padding: '8px 12px',
                            color: '#9ca3af',
                            whiteSpace: 'nowrap',
                          }}
                        >
                          {cell}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* No Results */}
          {result.success && result.rows.length === 0 && (
            <div
              style={{
                padding: '32px',
                textAlign: 'center',
                color: '#6b7280',
                fontSize: '13px',
              }}
            >
              No results returned
            </div>
          )}
        </div>
      )}
    </div>
  );
}
