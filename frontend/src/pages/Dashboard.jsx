import { useState, useEffect } from 'react';
import { Activity, ArrowDownRight, ArrowUpRight, Cpu, GitBranch, Layers, Zap, ArrowLeft } from 'lucide-react';
import { mockStats, mockAppBreakdown, mockFlows, formatBytes, getAppClass } from '../data/mockAnalysis';
import { Link } from 'react-router-dom';

function AnimatedNumber({ value }) {
  return <span>{value.toLocaleString()}</span>;
}

export default function Dashboard() {
  const [realResults, setRealResults] = useState(() => {
    try {
      const saved = localStorage.getItem('dpi_results');
      if (!saved) return null;
      const parsed = JSON.parse(saved);

      // Force mathematical consistency for the display
      if (parsed && Array.isArray(parsed.flows)) {
        let total = 0;
        let dropped = 0;
        parsed.flows.forEach(f => {
          if (f) {
            const pkts = Number(f.packets || 0);
            total += pkts;
            if (f.blocked) dropped += pkts;
          }
        });

        if (!parsed.stats) parsed.stats = {};
        parsed.stats.totalPackets = total;
        parsed.stats.dropped = dropped;
        parsed.stats.forwarded = total - dropped;
      }
      return parsed;
    } catch { return null; }
  });

  const flows = Array.isArray(realResults?.flows) ? realResults.flows : (realResults ? [] : mockFlows);
  const stats = realResults?.stats || mockStats;
  const appBreakdown = Array.isArray(realResults?.appBreakdown) ? realResults.appBreakdown : (realResults ? [] : mockAppBreakdown);
  const isRealData = !!realResults;
  const blockedFlows = Array.isArray(flows) ? flows.filter(f => f?.blocked).length :0;
  const totalPackets = (stats && stats.totalPackets) || 1;

  return (
    <div className="fade-in">
      {/* Back button */}
      <Link
        to="/"
        className="btn btn-ghost btn-sm"
        style={{ marginBottom: 16, display: 'inline-flex', alignItems: 'center', gap: 6, color: 'var(--text-3)', textDecoration: 'none' }}
      >
        <ArrowLeft size={16} />
        Back to Home
      </Link>

      {/* Header */}
      <div className="page-header" style={{ marginBottom: 32 }}>
        <div className="flex items-center gap-3 mb-2">
          <Cpu size={28} style={{ color: 'var(--accent-cyan)', filter: 'drop-shadow(0 0 8px var(--accent-cyan))' }} />
          <h1 className="page-title" style={{ fontSize: 30 }}>
            <span className="gradient-text">NetFilterX</span> Dashboard
          </h1>
        </div>
        <p className="page-subtitle">
          Real-time deep packet inspection · Multi-threaded · SNI-aware · Application-layer filtering
        </p>
        <div className="flex gap-2 mt-4" style={{ alignItems: 'center' }}>
          <Link to="/analyzer" className="btn btn-primary">
            <Zap size={16} /> Run Analysis
          </Link>
          <Link to="/rules" className="btn btn-secondary">
            <Layers size={16} /> Manage Rules
          </Link>
          {isRealData && (
            <span className="badge badge-green" style={{ fontSize: 11 }}>● Live Results</span>
          )}
          {!isRealData && (
            <span className="badge badge-muted" style={{ fontSize: 11 }}>Preview Data</span>
          )}
        </div>
      </div>

      {/* 4 Stat boxes from Home page */}
      <div className="grid-4 mb-8">
        <div className="card" style={{ textAlign: 'center', padding: '20px' }}>
          <div style={{ color: 'var(--accent-cyan)', marginBottom: 8 }}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
            </svg>
          </div>
          <div className="stat-value" style={{ fontSize: 28, fontFamily: 'var(--font-display)' }}>10Gbps</div>
          <div className="stat-label">Throughput</div>
        </div>
        <div className="card" style={{ textAlign: 'center', padding: '20px' }}>
          <div style={{ color: 'var(--accent-purple)', marginBottom: 8 }}>
            <Zap size={24} />
          </div>
          <div className="stat-value" style={{ fontSize: 28, fontFamily: 'var(--font-display)' }}>{'<1ms'}</div>
          <div className="stat-label">Latency</div>
        </div>
        <div className="card" style={{ textAlign: 'center', padding: '20px' }}>
          <div style={{ color: 'var(--accent-green)', marginBottom: 8 }}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
              <polyline points="22 4 22 11.08 14.92 11.08"/>
              <path d="M22 12A10 10 0 0 1 12 22a10 10 0 0 1-7.07-2.93"/>
              <polyline points="2 12 8 12 8 18"/>
            </svg>
          </div>
          <div className="stat-value" style={{ fontSize: 28, fontFamily: 'var(--font-display)' }}>99.9%</div>
          <div className="stat-label">Accuracy</div>
        </div>
        <div className="card" style={{ textAlign: 'center', padding: '20px' }}>
          <div style={{ color: 'var(--accent-orange)', marginBottom: 8 }}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10"/>
              <line x1="2" y1="12" x2="22" y2="12"/>
              <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
            </svg>
          </div>
          <div className="stat-value" style={{ fontSize: 28, fontFamily: 'var(--font-display)' }}>50+</div>
          <div className="stat-label">Protocols</div>
        </div>
      </div>

      {/* Stat cards */}
      <div className="grid-4 mb-8">
        <div className="stat-card" style={{ animationDelay: '0ms' }}>
          <div className="stat-icon stat-icon-cyan"><Activity size={22} /></div>
          <div className="stat-info">
            <div className="stat-label">Total Packets</div>
            <div className="stat-value"><AnimatedNumber value={stats.totalPackets} /></div>
            <div className="stat-sub">{formatBytes(stats.totalBytes)} processed</div>
          </div>
        </div>
        <div className="stat-card" style={{ animationDelay: '80ms' }}>
          <div className="stat-icon stat-icon-green"><ArrowUpRight size={22} /></div>
          <div className="stat-info">
            <div className="stat-label">Forwarded</div>
            <div className="stat-value" style={{ color: 'var(--accent-green)' }}>
              <AnimatedNumber value={stats.forwarded} />
            </div>
            <div className="stat-sub">{((stats.forwarded / totalPackets) * 100).toFixed(1)}% pass rate</div>
          </div>
        </div>
        <div className="stat-card" style={{ animationDelay: '160ms' }}>
          <div className="stat-icon stat-icon-red"><ArrowDownRight size={22} /></div>
          <div className="stat-info">
            <div className="stat-label">Dropped</div>
            <div className="stat-value" style={{ color: 'var(--accent-red)' }}>
              <AnimatedNumber value={stats.dropped} />
            </div>
            <div className="stat-sub">{((stats.dropped / totalPackets) * 100).toFixed(1)}% blocked</div>
          </div>
        </div>
        <div className="stat-card" style={{ animationDelay: '240ms' }}>
          <div className="stat-icon stat-icon-purple"><GitBranch size={22} /></div>
          <div className="stat-info">
            <div className="stat-label">Active Flows</div>
            <div className="stat-value"><AnimatedNumber value={stats.activeFlows} /></div>
            <div className="stat-sub">{blockedFlows} flows blocked</div>
          </div>
        </div>
      </div>

      {/* App breakdown + recent flows */}
      <div className="grid-2 mb-8">
        {/* App Breakdown */}
        <div className="card card-cyan">
          <div className="section-title"><Layers size={16} style={{ color: 'var(--accent-cyan)' }} /> Application Breakdown</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {appBreakdown.slice(0, 8).map(app => {
              const pct = ((app.packets / totalPackets) * 100).toFixed(1);
              return (
                <div key={app.name}>
                  <div className="flex justify-between mb-1" style={{ fontSize: 13 }}>
                    <span style={{ color: app.color, fontWeight: 600 }}>{app.name}</span>
                    <span className="text-secondary">{app.packets.toLocaleString()} pkts · {pct}%</span>
                  </div>
                  <div className="progress-bar-wrap">
                    <div
                      className="progress-bar-fill"
                      style={{
                        width: `${pct}%`,
                        background: `linear-gradient(90deg, ${app.color}cc, ${app.color})`,
                        boxShadow: `0 0 8px ${app.color}55`,
                      }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Recent Detections */}
        <div className="card">
          <div className="section-title"><Activity size={16} style={{ color: 'var(--accent-purple)' }} /> Recent Detections</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {flows.slice(0, 9).map(flow => (
              <div
                key={flow.id}
                className="flex items-center justify-between"
                style={{
                  padding: '8px 12px',
                  borderRadius: 'var(--radius-sm)',
                  background: flow.blocked ? 'var(--accent-red-dim)' : 'var(--bg-800)',
                  border: `1px solid ${flow.blocked ? 'rgba(239,68,68,0.2)' : 'var(--border-subtle)'}`,
                }}
              >
                <div>
                  <span
                    className={getAppClass(flow.app)}
                    style={{ fontWeight: 600, fontSize: 13 }}
                  >
                    {flow.app}
                  </span>
                  {flow.sni && (
                    <span className="text-muted font-mono" style={{ fontSize: 11, marginLeft: 8 }}>
                      {flow.sni}
                    </span>
                  )}
                </div>
                <span className={`badge ${flow.blocked ? 'badge-red' : 'badge-green'}`}>
                  {flow.blocked ? 'Blocked' : 'Fwd'}
                </span>
              </div>
            ))}
          </div>

          <Link to="/flows" className="btn btn-ghost btn-sm w-full mt-4" style={{ justifyContent: 'center' }}>
            View all {flows.length} flows →
          </Link>
        </div>
      </div>

      {/* Engine info bar */}
      <div className="card" style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 0 }}>
        {[
          { label: 'Processing Speed', value: stats.processingTimeMs ? `${stats.processingTimeMs}ms` : 'N/A', sub: 'last analysis' },
          { label: 'TCP Packets', value: (stats.tcpPackets || 0).toLocaleString(), sub: 'transport layer' },
          { label: 'UDP Packets', value: (stats.udpPackets || 0).toLocaleString(), sub: 'transport layer' },
          { label: 'Architecture', value: 'Multi-thread', sub: '2 LBs · 4 FPs' },
        ].map((item, i) => (
          <div
            key={item.label}
            style={{
              padding: '16px 20px',
              borderRight: i < 3 ? '1px solid var(--border-subtle)' : 'none',
            }}
          >
            <div className="stat-label mb-1">{item.label}</div>
            <div className="font-bold" style={{ fontSize: 20, color: 'var(--accent-cyan)' }}>{item.value}</div>
            <div className="text-muted text-xs">{item.sub}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
