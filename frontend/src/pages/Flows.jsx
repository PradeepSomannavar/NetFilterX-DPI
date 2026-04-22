import { useState, useEffect, useMemo } from 'react';
import { Network, Search, ChevronDown, ChevronUp, ArrowUpDown, Activity, Shield, BarChart3, AlertCircle } from 'lucide-react';
import { formatBytes, getAppClass } from '../data/mockAnalysis';

export default function Flows() {
  const [results, setResults] = useState(null);
  const [search, setSearch] = useState('');
  const [sortKey, setSortKey] = useState('packets');
  const [sortDir, setSortDir] = useState('desc');
  const [error, setError] = useState(null);

  // Load results from localStorage
  useEffect(() => {
    try {
      const saved = localStorage.getItem('dpi_results');
      if (saved) {
        const parsed = JSON.parse(saved);
        console.log("Flows page loaded data:", parsed);
        setResults(parsed);
      }
    } catch (e) {
      console.error("Failed to parse dpi_results", e);
      setError("Failed to load flow data from storage.");
    }
  }, []);

  const baseFlows = useMemo(() => {
    try {
      if (!results) return [];
      // Handle potential case sensitivity or missing keys
      const f = results.flows || results.Flows || results.data?.flows || [];
      return Array.isArray(f) ? f : [];
    } catch (e) {
      console.error("Error extracting flows from results", e);
      return [];
    }
  }, [results]);

  const flows = useMemo(() => {
    try {
      let list = [...baseFlows];

      // Filter
      if (search) {
        const s = search.toLowerCase();
        list = list.filter(f => {
          if (!f) return false;
          const app = String(f.app || '').toLowerCase();
          const src = String(f.srcIp || '').toLowerCase();
          const dst = String(f.dstIp || '').toLowerCase();
          const sni = String(f.sni || '').toLowerCase();
          return app.includes(s) || src.includes(s) || dst.includes(s) || sni.includes(s);
        });
      }

      // Sort
      list.sort((a, b) => {
        if (!a || !b) return 0;
        let av = a[sortKey];
        let bv = b[sortKey];

        if (av === undefined || av === null) av = '';
        if (bv === undefined || bv === null) bv = '';

        if (typeof av === 'string') {
          return sortDir === 'asc' ? av.localeCompare(String(bv)) : String(bv).localeCompare(av);
        }
        return sortDir === 'asc' ? av - bv : bv - av;
      });

      return list;
    } catch (e) {
      console.error("Error processing flows (filter/sort)", e);
      return baseFlows;
    }
  }, [baseFlows, search, sortKey, sortDir]);

  const toggleSort = (key) => {
    if (sortKey === key) {
      setSortDir(sortDir === 'asc' ? 'desc' : 'asc');
    } else {
      setSortKey(key);
      setSortDir('desc');
    }
  };

  const SortIcon = ({ k }) => {
    if (sortKey !== k) return <ArrowUpDown size={12} className="ml-1 opacity-30" />;
    return sortDir === 'asc' ? <ChevronUp size={12} className="ml-1 text-cyan" /> : <ChevronDown size={12} className="ml-1 text-cyan" />;
  };

  // Stats calculation
  const { blocked, totalPackets, avgPackets } = useMemo(() => {
    if (!baseFlows.length) return { blocked: 0, totalPackets: 0, avgPackets: "0.0" };
    let bCount = 0;
    let pCount = 0;
    baseFlows.forEach(f => {
      if (f?.blocked) bCount++;
      pCount += Number(f?.packets || 0);
    });
    return {
      blocked: bCount,
      totalPackets: pCount,
      avgPackets: (pCount / baseFlows.length).toFixed(1)
    };
  }, [baseFlows]);

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center p-20 text-center">
        <AlertCircle size={48} color="var(--accent-red)" className="mb-4" />
        <h2 className="text-xl font-bold mb-2">Something went wrong</h2>
        <p className="text-secondary">{error}</p>
        <button className="btn btn-primary mt-4" onClick={() => window.location.reload()}>Retry</button>
      </div>
    );
  }

  if (!results) {
    return (
      <div className="flex flex-col items-center justify-center p-20 text-center fade-in">
        <div className="p-6 rounded-full bg-slate-800/50 mb-6 border border-slate-700">
          <Network size={40} className="text-slate-500" />
        </div>
        <h2 className="text-2xl font-bold mb-2 text-white">No Flow Data Available</h2>
        <p className="text-secondary max-w-md">
          Run an analysis on the <span className="text-cyan">Analyzer</span> page to see real-time flow classifications and tracking here.
        </p>
      </div>
    );
  }

  return (
    <div className="page-container flows-page fade-in">
      <div className="flex justify-between items-end mb-6">
        <div>
          <h1 className="page-title">Flow <span className="gradient-text">Analysis</span></h1>
          <p className="page-subtitle">Real-time connection tracking and application classification</p>
        </div>
        <div className="search-wrap">
          <Search size={18} className="search-icon" />
          <input
            type="text"
            className="search-input"
            placeholder="Search IP, application or SNI..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      {/* Mini stats */}
      <div className="grid-4 mb-6">
        <div className="stat-card">
          <div className="stat-icon stat-icon-cyan"><Activity size={20} /></div>
          <div className="stat-content">
            <div className="stat-label">Total Flows</div>
            <div className="stat-value">{baseFlows.length}</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon stat-icon-green"><Shield size={20} /></div>
          <div className="stat-content">
            <div className="stat-label">Forwarded</div>
            <div className="stat-value text-green">{baseFlows.length - blocked}</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon stat-icon-red"><Shield size={20} /></div>
          <div className="stat-content">
            <div className="stat-label">Blocked</div>
            <div className="stat-value text-red">{blocked}</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon stat-icon-purple"><BarChart3 size={20} /></div>
          <div className="stat-content">
            <div className="stat-label">Avg Packets/Flow</div>
            <div className="stat-value">{avgPackets}</div>
          </div>
        </div>
      </div>

      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <div className="table-container">
          <table className="flows-table">
            <thead>
              <tr>
                <th onClick={() => toggleSort('app')}>App <SortIcon k="app" /></th>
                <th onClick={() => toggleSort('srcIp')}>Source <SortIcon k="srcIp" /></th>
                <th onClick={() => toggleSort('dstIp')}>Destination <SortIcon k="dstIp" /></th>
                <th onClick={() => toggleSort('protocol')}>Proto <SortIcon k="protocol" /></th>
                <th onClick={() => toggleSort('sni')}>SNI / Host <SortIcon k="sni" /></th>
                <th onClick={() => toggleSort('packets')}>Packets <SortIcon k="packets" /></th>
                <th onClick={() => toggleSort('bytes')}>Bytes <SortIcon k="bytes" /></th>
                <th onClick={() => toggleSort('blocked')}>Status <SortIcon k="blocked" /></th>
              </tr>
            </thead>
            <tbody>
              {flows.length > 0 ? (
                flows.map((flow, idx) => {
                  if (!flow) return null;
                  try {
                    return (
                      <tr key={flow.id || `flow-${idx}`} className={flow.blocked ? 'row-blocked' : ''}>
                        <td>
                          <span className={getAppClass(flow.app)}>
                            {flow.app || 'Unknown'}
                          </span>
                        </td>
                        <td className="mono" style={{ fontSize: 12 }}>
                          {flow.srcIp || '?.?.?.?'}
                          <span className="text-muted ml-1" style={{ fontSize: 10 }}>:{flow.srcPort || '0'}</span>
                        </td>
                        <td className="mono" style={{ fontSize: 12 }}>
                          {flow.dstIp || '?.?.?.?'}
                          <span className="text-muted ml-1" style={{ fontSize: 10 }}>:{flow.dstPort || '0'}</span>
                        </td>
                        <td>
                          <span className="badge badge-muted" style={{ fontSize: 10 }}>{flow.protocol || 'TCP'}</span>
                        </td>
                        <td className="mono text-muted" style={{ fontSize: 11 }}>{flow.sni || '-'}</td>
                        <td className="text-right font-medium">{Number(flow.packets || 0).toLocaleString()}</td>
                        <td className="text-right text-secondary">{formatBytes(flow.bytes || 0)}</td>
                        <td>
                          <span className={`badge ${flow.blocked ? 'badge-red' : 'badge-green'}`}>
                            {flow.blocked ? 'Blocked' : 'Forwarded'}
                          </span>
                        </td>
                      </tr>
                    );
                  } catch (e) {
                    console.error("Error rendering flow row", e, flow);
                    return null;
                  }
                })
              ) : (
                <tr>
                  <td colSpan="8" className="text-center p-10 text-secondary">
                    {search ? `No flows matching "${search}"` : 'No flows detected in this analysis.'}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
