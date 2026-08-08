// DataGrid component - Virtualized grid for displaying query results

import React, { useMemo } from 'react';
import { ChevronLeft, ChevronRight, Download, Filter } from 'lucide-react';

interface DataGridProps {
  columns: string[];
  rows: string[][];
  loading?: boolean;
  pageSize?: number;
}

export default function DataGrid({ columns, rows, loading = false, pageSize = 50 }: DataGridProps) {
  const [currentPage, setCurrentPage] = React.useState(0);
  const [sortColumn, setSortColumn] = React.useState<string | null>(null);
  const [sortDirection, setSortDirection] = React.useState<'asc' | 'desc'>('asc');
  const [filters, setFilters] = React.useState<Record<string, string>>({});

  // Apply sorting and filtering
  const processedData = useMemo(() => {
    let data = [...rows];

    // Apply filters
    Object.entries(filters).forEach(([colIndex, filterValue]) => {
      if (filterValue) {
        data = data.filter(row => 
          row[parseInt(colIndex)].toLowerCase().includes(filterValue.toLowerCase())
        );
      }
    });

    // Apply sorting
    if (sortColumn !== null) {
      const colIndex = columns.indexOf(sortColumn);
      if (colIndex !== -1) {
        data.sort((a, b) => {
          const aVal = a[colIndex];
          const bVal = b[colIndex];
          
          // Try numeric comparison
          const aNum = parseFloat(aVal);
          const bNum = parseFloat(bVal);
          
          if (!isNaN(aNum) && !isNaN(bNum)) {
            return sortDirection === 'asc' ? aNum - bNum : bNum - aNum;
          }
          
          // String comparison
          return sortDirection === 'asc' 
            ? aVal.localeCompare(bVal)
            : bVal.localeCompare(aVal);
        });
      }
    }

    return data;
  }, [rows, filters, sortColumn, sortDirection, columns]);

  // Pagination
  const totalPages = Math.ceil(processedData.length / pageSize);
  const paginatedData = processedData.slice(
    currentPage * pageSize,
    (currentPage + 1) * pageSize
  );

  const handleSort = (column: string) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(column);
      setSortDirection('asc');
    }
  };

  const handleFilter = (colIndex: number, value: string) => {
    setFilters(prev => ({
      ...prev,
      [colIndex]: value
    }));
    setCurrentPage(0); // Reset to first page on filter
  };

  const handleExport = () => {
    const csv = [
      columns.join(','),
      ...processedData.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'query_results.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <div
        style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '300px',
          color: '#6b7280',
          fontSize: '14px',
        }}
      >
        Loading data...
      </div>
    );
  }

  if (rows.length === 0) {
    return (
      <div
        style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '300px',
          color: '#6b7280',
          fontSize: '14px',
        }}
      >
        No data to display
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Toolbar */}
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
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <span style={{ color: '#9ca3af', fontSize: '12px' }}>
            {processedData.length} rows
          </span>
          {processedData.length !== rows.length && (
            <span style={{ color: '#f59e0b', fontSize: '12px' }}>
              (filtered from {rows.length} total)
            </span>
          )}
        </div>

        <button
          onClick={handleExport}
          style={{
            background: '#4a4a4a',
            border: 'none',
            borderRadius: '4px',
            padding: '6px 12px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            color: '#e0e0e0',
            fontSize: '12px',
          }}
        >
          <Download size={14} />
          Export CSV
        </button>
      </div>

      {/* Table */}
      <div style={{ flex: 1, overflow: 'auto' }}>
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
              {columns.map((column, index) => (
                <th
                  key={index}
                  style={{
                    padding: '8px 12px',
                    textAlign: 'left',
                    borderBottom: '1px solid #4a4a4a',
                    color: '#e0e0e0',
                    fontWeight: '500',
                    whiteSpace: 'nowrap',
                    cursor: 'pointer',
                    userSelect: 'none',
                  }}
                  onClick={() => handleSort(column)}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    {column}
                    {sortColumn === column && (
                      <span style={{ color: '#3b82f6', fontSize: '10px' }}>
                        {sortDirection === 'asc' ? '↑' : '↓'}
                      </span>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {paginatedData.map((row, rowIndex) => (
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

      {/* Filter Row */}
      <div
        style={{
          padding: '8px 16px',
          borderBottom: '1px solid #4a4a4a',
          background: '#252525',
          display: 'flex',
          gap: '8px',
          overflow: 'auto',
        }}
      >
        {columns.map((column, index) => (
          <div
            key={index}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              minWidth: '120px',
            }}
          >
            <Filter size={12} style={{ color: '#6b7280' }} />
            <input
              type="text"
              placeholder={`Filter ${column}...`}
              value={filters[index] || ''}
              onChange={(e) => handleFilter(index, e.target.value)}
              style={{
                flex: 1,
                background: '#1e1e1e',
                border: '1px solid #4a4a4a',
                borderRadius: '4px',
                padding: '4px 8px',
                color: '#e0e0e0',
                fontSize: '11px',
                fontFamily: 'monospace',
                outline: 'none',
                minWidth: '100px',
              }}
            />
          </div>
        ))}
      </div>

      {/* Pagination */}
      <div
        style={{
          padding: '12px 16px',
          borderTop: '1px solid #4a4a4a',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          background: '#2d2d2d',
        }}
      >
        <div style={{ color: '#9ca3af', fontSize: '12px' }}>
          Page {currentPage + 1} of {totalPages || 1}
        </div>

        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            onClick={() => setCurrentPage(Math.max(0, currentPage - 1))}
            disabled={currentPage === 0}
            style={{
              background: currentPage === 0 ? '#3a3a3a' : '#4a4a4a',
              border: 'none',
              borderRadius: '4px',
              padding: '6px 12px',
              cursor: currentPage === 0 ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              color: '#e0e0e0',
              fontSize: '12px',
              opacity: currentPage === 0 ? 0.5 : 1,
            }}
          >
            <ChevronLeft size={14} />
            Previous
          </button>

          <button
            onClick={() => setCurrentPage(Math.min(totalPages - 1, currentPage + 1))}
            disabled={currentPage >= totalPages - 1}
            style={{
              background: currentPage >= totalPages - 1 ? '#3a3a3a' : '#4a4a4a',
              border: 'none',
              borderRadius: '4px',
              padding: '6px 12px',
              cursor: currentPage >= totalPages - 1 ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              color: '#e0e0e0',
              fontSize: '12px',
              opacity: currentPage >= totalPages - 1 ? 0.5 : 1,
            }}
          >
            Next
            <ChevronRight size={14} />
          </button>
        </div>
      </div>
    </div>
  );
}
