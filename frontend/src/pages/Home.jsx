import { Link } from 'react-router-dom';
import {
  Zap,
  BarChart3,
  Network,
  ArrowRight,
  CheckCircle2,
  Shield,
  Activity,
  Cpu,
} from 'lucide-react';

const features = [
  {
    icon: Shield,
    colorClass: 'feature-icon-cyan',
    title: 'Deep Packet Inspection',
    desc: 'Layer 7 application identification using SNI extraction and HTTP Host analysis. Classify traffic with precision across encrypted and plain-text protocols.',
  },
  {
    icon: Zap,
    colorClass: 'feature-icon-coral',
    title: 'Real-Time Analysis',
    desc: 'Sub-second latency analysis with live traffic streaming. Monitor network flows as they happen with instantaneous SNI extraction and classification.',
  },
  {
    icon: BarChart3,
    colorClass: 'feature-icon-blue',
    title: 'Traffic Analytics',
    desc: 'Detailed breakdowns of bandwidth usage, protocol distribution, and flow states. Visualize network behavior through interactive charts and dashboards.',
  },
  {
    icon: Network,
    colorClass: 'feature-icon-green',
    title: 'Flow Tracking',
    desc: 'Track network flows with stateful inspection. Monitor active connections, session duration, and application-level metadata.',
  },
  {
    icon: Activity,
    colorClass: 'feature-icon-warning',
    title: 'Rule Engine',
    desc: 'Define custom DPI rules with a flexible engine. Block, throttle, or reroute traffic based on application, protocol, or payload patterns.',
  },
  {
    icon: CheckCircle2,
    colorClass: 'feature-icon-danger',
    title: 'Threat Detection',
    desc: 'Identify malicious patterns, anomalies, and policy violations. Get actionable alerts with context-rich packet details.',
  },
];

const stats = [
  { value: '10Gbps', label: 'Throughput' },
  { value: '<1ms', label: 'Latency' },
  { value: '99.9%', label: 'Accuracy' },
  { value: '50+', label: 'Protocols' },
];

export default function Home() {
  return (
    <div className="home-container fade-in">
      {/* Hero Section */}
      <section className="hero">
        <div className="hero-badge">
          <Cpu size={14} />
          NetFilterX v2.0 — Policy-Driven DPI & Traffic Enforcement
        </div>

        <h1 className="hero-title">
          Deep Packet <span className="gradient-text">Inspection Engine</span>
        </h1>

        <p className="hero-subtitle">
          Layer 7 application identification, real-time policy enforcement, and traffic analytics.
          Built for networks that demand deep visibility and control.
        </p>

        <div className="hero-actions">
          <Link to="/dashboard" className="btn btn-lg btn-primary">
            <Zap size={18} />
            Get Started
            <ArrowRight size={16} />
          </Link>
          <Link to="/dashboard" className="btn btn-lg btn-outline">
            <BarChart3 size={18} />
            Live Dashboard
          </Link>
        </div>

        {/* Stats Row */}
        <div className="features-grid" style={{ marginTop: 'var(--sp-12)', gridTemplateColumns: 'repeat(4, 1fr)' }}>
          {stats.map((s) => (
            <div key={s.label} className="card" style={{ textAlign: 'center', padding: 'var(--sp-5)' }}>
              <div className="stat-value" style={{ fontSize: '28px', fontFamily: 'var(--font-display)' }}>{s.value}</div>
              <div className="stat-label">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Divider */}
      <div className="divider" style={{ margin: 'var(--sp-12) 0' }} />

      {/* Features Section */}
      <section>
        <h2 className="h2" style={{ textAlign: 'center', marginBottom: 'var(--sp-2)' }}>
          Built for <span className="gradient-text">Performance</span>
        </h2>
        <p className="body-lg" style={{ textAlign: 'center', color: 'var(--text-3)', maxWidth: '600px', margin: '0 auto var(--sp-8)' }}>
          From packet capture to policy enforcement — everything you need to inspect, analyze, and control network traffic at scale.
        </p>

        <div className="features-grid">
          {features.map((f) => (
            <div key={f.title} className="feature-card">
              <div className={`feature-icon ${f.colorClass}`}>
                <f.icon size={24} />
              </div>
              <h3 className="feature-title">{f.title}</h3>
              <p className="feature-desc">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Bottom CTA */}
      <section style={{ textAlign: 'center', padding: 'var(--sp-16) 0 var(--sp-8)' }}>
        <h2 className="h2" style={{ marginBottom: 'var(--sp-4)' }}>
          Ready to inspect your network?
        </h2>
        <p className="body-lg" style={{ color: 'var(--text-3)', marginBottom: 'var(--sp-6)', maxWidth: '500px', margin: '0 auto var(--sp-6)' }}>
          Upload a PCAP file or connect a live interface to start analyzing traffic in seconds.
        </p>
        <Link to="/dashboard" className="btn btn-lg btn-primary">
          <Zap size={18} />
          Launch Analyzer
          <ArrowRight size={16} />
        </Link>
        <div style={{ marginTop: 'var(--sp-6)', display: 'flex', justifyContent: 'center', gap: 'var(--sp-6)', flexWrap: 'wrap' }}>
          {['libpcap v1.10', 'FastAPI Backend', 'React + Vite', 'Python + Scapy'].map((tag) => (
            <span key={tag} className="caption" style={{ display: 'flex', alignItems: 'center', gap: 'var(--sp-1)' }}>
              <CheckCircle2 size={12} style={{ color: 'var(--accent)' }} />
              {tag}
            </span>
          ))}
        </div>
      </section>
    </div>
  );
}
