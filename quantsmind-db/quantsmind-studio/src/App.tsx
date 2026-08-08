// Main App component - QuantsMind Studio application shell

import React, { useState, useCallback } from 'react';
import { ReactFlowProvider } from 'reactflow';
import 'reactflow/dist/style.css';
import Canvas from './components/Canvas';
import QueryEditor from './components/QueryEditor';
import DataGrid from './components/DataGrid';
import { Database, Settings, Layout, Code, Table, LogOut } from 'lucide-react';
import { invoke } from '@tauri-apps/api/core';

type View = 'canvas' | 'query' | 'data' | 'settings';

interface QueryResult {
  success: boolean;
  message: string;
  rows: string[][];
  columns: string[];
  executionTimeMs: number;
}

export default function App() {
  const [currentView, setCurrentView] = useState<View>('canvas');
  const [isConnected, setIsConnected] = useState(false);
  const [connectionString, setConnectionString] = useState('quantsmind.db');
  const [queryResult, setQueryResult] = useState<QueryResult | null>(null);

  const handleConnect = useCallback(async () => {
    try {
      const success = await invoke<boolean>('connect_database', { connectionString });
      setIsConnected(success);
    } catch (error) {
      console.error('Connection error:', error);
    }
  }, [connectionString]);

  const handleDisconnect = useCallback(async () => {
    try {
      await invoke('disconnect_database');
      setIsConnected(false);
      setQueryResult(null);
    } catch (error) {
      console.error('Disconnect error:', error);
    }
  }, []);

  const handleExecuteQuery = useCallback(async (sql: string) => {
    try {
      const result = await invoke<QueryResult>('execute_query', { request: { sql } });
      setQueryResult(result);
      return result;
    } catch (error) {
      const errorResult: QueryResult = {
        success: false,
        message: error instanceof Error ? error.message : 'Unknown error',
        rows: [],
        columns: [],
        executionTimeMs: 0,
      };
      setQueryResult(errorResult);
      return errorResult;
    }
  }, []);

  const handleExecuteDDL = useCallback(async (sql: string) => {
    try {
      await invoke('execute_ddl', { sql });
      return true;
    } catch (error) {
      console.error('DDL execution error:', error);
      return false;
    }
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', background: '#1a1a1a', color: '#e0e0e0', fontFamily: 'system-ui, -apple-system, sans-serif' }}>
      {/* Header */}
      <header
        style={{
          padding: '16px 24px',
          borderBottom: '1px solid #4a4a4a',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          background: '#2d2d2d',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <Database size={24} style={{ color: '#3b82f6' }} />
          <div>
            <h1 style={{ margin: 0, fontSize: '20px', fontWeight: '600', color: '#e0e0e0' }}>
              QuantsMind Studio
            </h1>
            <p style={{ margin: 0, fontSize: '12px', color: '#9ca3af' }}>
              Visual Database Development Environment
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <input
            type="text"
            value={connectionString}
            onChange={(e) => setConnectionString(e.target.value)}
            placeholder="Database path (e.g., quantsmind.db)"
            style={{
              background: '#1e1e1e',
              border: '1px solid #4a4a4a',
              borderRadius: '6px',
              padding: '8px 12px',
              color: '#e0e0e0',
              fontSize: '13px',
              width: '250px',
              outline: 'none',
            }}
          />

          {!isConnected ? (
            <button
              onClick={handleConnect}
              style={{
                background: '#3b82f6',
                border: 'none',
                borderRadius: '6px',
                padding: '8px 16px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                color: 'white',
                fontSize: '13px',
                fontWeight: '500',
              }}
            >
              <Database size={16} />
              Connect
            </button>
          ) : (
            <button
              onClick={handleDisconnect}
              style={{
                background: '#ef4444',
                border: 'none',
                borderRadius: '6px',
                padding: '8px 16px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                color: 'white',
                fontSize: '13px',
                fontWeight: '500',
              }}
            >
              <LogOut size={16} />
              Disconnect
            </button>
          )}
        </div>
      </header>

      {/* Navigation */}
      <nav
        style={{
          padding: '0 24px',
          borderBottom: '1px solid #4a4a4a',
          display: 'flex',
          gap: '4px',
          background: '#252525',
        }}
      >
        {[
          { id: 'canvas' as View, label: 'Schema Designer', icon: Layout },
          { id: 'query' as View, label: 'Query Editor', icon: Code },
          { id: 'data' as View, label: 'Data Grid', icon: Table },
          { id: 'settings' as View, label: 'Settings', icon: Settings },
        ].map((item) => (
          <button
            key={item.id}
            onClick={() => setCurrentView(item.id)}
            style={{
              background: currentView === item.id ? '#3b82f6' : 'transparent',
              border: 'none',
              borderRadius: '6px 6px 0 0',
              padding: '12px 16px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              color: currentView === item.id ? 'white' : '#9ca3af',
              fontSize: '13px',
              fontWeight: currentView === item.id ? '500' : '400',
              borderBottom: currentView === item.id ? '2px solid #3b82f6' : '2px solid transparent',
              marginBottom: '-1px',
            }}
          >
            <item.icon size={16} />
            {item.label}
          </button>
        ))}
      </nav>

      {/* Main Content */}
      <main style={{ flex: 1, overflow: 'hidden' }}>
        {currentView === 'canvas' && (
          <ReactFlowProvider>
            <Canvas />
          </ReactFlowProvider>
        )}

        {currentView === 'query' && (
          <QueryEditor
            onExecute={handleExecuteQuery}
            isConnected={isConnected}
          />
        )}

        {currentView === 'data' && (
          <div style={{ padding: '24px', height: '100%' }}>
            {queryResult && queryResult.success ? (
              <DataGrid
                columns={queryResult.columns}
                rows={queryResult.rows}
              />
            ) : (
              <div
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'center',
                  alignItems: 'center',
                  height: '100%',
                  color: '#6b7280',
                  fontSize: '14px',
                }}
              >
                <Database size={48} style={{ marginBottom: '16px', opacity: 0.5 }} />
                <p>No query results to display</p>
                <p style={{ fontSize: '12px', marginTop: '8px' }}>
                  Execute a query in the Query Editor to see results here
                </p>
              </div>
            )}
          </div>
        )}

        {currentView === 'settings' && (
          <div style={{ padding: '24px' }}>
            <h2 style={{ margin: '0 0 24px 0', fontSize: '18px', color: '#e0e0e0' }}>
              Settings
            </h2>

            <div
              style={{
                background: '#2d2d2d',
                borderRadius: '8px',
                padding: '20px',
                maxWidth: '600px',
              }}
            >
              <h3 style={{ margin: '0 0 16px 0', fontSize: '14px', color: '#e0e0e0' }}>
                Database Configuration
              </h3>

              <div style={{ marginBottom: '16px' }}>
                <label
                  style={{
                    display: 'block',
                    marginBottom: '8px',
                    fontSize: '12px',
                    color: '#9ca3af',
                  }}
                >
                  Default Database Path
                </label>
                <input
                  type="text"
                  defaultValue="quantsmind.db"
                  style={{
                    width: '100%',
                    background: '#1e1e1e',
                    border: '1px solid #4a4a4a',
                    borderRadius: '4px',
                    padding: '8px 12px',
                    color: '#e0e0e0',
                    fontSize: '13px',
                    outline: 'none',
                  }}
                />
              </div>

              <div style={{ marginBottom: '16px' }}>
                <label
                  style={{
                    display: 'block',
                    marginBottom: '8px',
                    fontSize: '12px',
                    color: '#9ca3af',
                  }}
                >
                  Buffer Pool Size (frames)
                </label>
                <input
                  type="number"
                  defaultValue="1024"
                  style={{
                    width: '100%',
                    background: '#1e1e1e',
                    border: '1px solid #4a4a4a',
                    borderRadius: '4px',
                    padding: '8px 12px',
                    color: '#e0e0e0',
                    fontSize: '13px',
                    outline: 'none',
                  }}
                />
              </div>

              <button
                style={{
                  background: '#3b82f6',
                  border: 'none',
                  borderRadius: '4px',
                  padding: '8px 16px',
                  cursor: 'pointer',
                  color: 'white',
                  fontSize: '13px',
                  fontWeight: '500',
                }}
              >
                Save Settings
              </button>
            </div>

            <div
              style={{
                marginTop: '24px',
                background: '#2d2d2d',
                borderRadius: '8px',
                padding: '20px',
                maxWidth: '600px',
              }}
            >
              <h3 style={{ margin: '0 0 16px 0', fontSize: '14px', color: '#e0e0e0' }}>
                About QuantsMind Studio
              </h3>
              <p style={{ margin: '0 0 8px 0', fontSize: '12px', color: '#9ca3af' }}>
                Version: 0.1.0
              </p>
              <p style={{ margin: '0 0 8px 0', fontSize: '12px', color: '#9ca3af' }}>
                A visual database development environment for QuantsMind
              </p>
              <p style={{ margin: 0, fontSize: '12px', color: '#9ca3af' }}>
                Built with Tauri v2, React, TypeScript, and React Flow
              </p>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer
        style={{
          padding: '8px 24px',
          borderTop: '1px solid #4a4a4a',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          background: '#2d2d2d',
          fontSize: '11px',
          color: '#6b7280',
        }}
      >
        <span>QuantsMind Studio v0.1.0</span>
        <span>
          {isConnected ? (
            <span style={{ color: '#10b981' }}>● Connected to {connectionString}</span>
          ) : (
            <span style={{ color: '#ef4444' }}>● Not connected</span>
          )}
        </span>
      </footer>
    </div>
  );
}
