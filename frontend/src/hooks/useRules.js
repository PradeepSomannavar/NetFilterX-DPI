/**
 * Shared hook for blocking rules — persisted in localStorage so state
 * survives navigation between Rules, Analyzer, and other tabs.
 */

import { useState } from 'react';
import { defaultBlockedApps, defaultBlockedIPs, defaultBlockedDomains } from '../data/mockAnalysis';

function loadFromStorage(key, fallback) {
  try {
    const raw = localStorage.getItem(key);
    return raw !== null ? JSON.parse(raw) : fallback;
  } catch {
    return fallback;
  }
}

export function useRules() {
  const [blockedApps, _setBlockedApps] = useState(() =>
    loadFromStorage('dpi_blocked_apps', defaultBlockedApps)
  );
  const [blockedIPs, _setBlockedIPs] = useState(() =>
    loadFromStorage('dpi_blocked_ips', defaultBlockedIPs)
  );
  const [blockedDomains, _setBlockedDomains] = useState(() =>
    loadFromStorage('dpi_blocked_domains', defaultBlockedDomains)
  );

  const setBlockedApps = (v) => {
    const next = typeof v === 'function' ? v(blockedApps) : v;
    localStorage.setItem('dpi_blocked_apps', JSON.stringify(next));
    _setBlockedApps(next);
  };

  const setBlockedIPs = (v) => {
    const next = typeof v === 'function' ? v(blockedIPs) : v;
    localStorage.setItem('dpi_blocked_ips', JSON.stringify(next));
    _setBlockedIPs(next);
  };

  const setBlockedDomains = (v) => {
    const next = typeof v === 'function' ? v(blockedDomains) : v;
    localStorage.setItem('dpi_blocked_domains', JSON.stringify(next));
    _setBlockedDomains(next);
  };

  const toggleApp = (app) =>
    setBlockedApps((prev) =>
      prev.includes(app) ? prev.filter((a) => a !== app) : [...prev, app]
    );

  const addIP = (ip) => {
    const v = ip.trim();
    if (v && !blockedIPs.includes(v)) setBlockedIPs((p) => [...p, v]);
  };

  const removeIP = (ip) => setBlockedIPs((p) => p.filter((x) => x !== ip));

  const addDomain = (domain) => {
    const v = domain.trim();
    if (v && !blockedDomains.includes(v)) setBlockedDomains((p) => [...p, v]);
  };

  const removeDomain = (d) => setBlockedDomains((p) => p.filter((x) => x !== d));

  return {
    blockedApps, setBlockedApps, toggleApp,
    blockedIPs, setBlockedIPs, addIP, removeIP,
    blockedDomains, setBlockedDomains, addDomain, removeDomain,
  };
}
