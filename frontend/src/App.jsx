import { BrowserRouter, Routes, Route, Outlet } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Home from './pages/Home';
import Dashboard from './pages/Dashboard';
import Analyzer from './pages/Analyzer';
import Traffic from './pages/Traffic';
import Rules from './pages/Rules';
import Flows from './pages/Flows';

function AppLayout() {
  return (
    <div className="app-layout">
      <Sidebar />
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Landing page — NO sidebar, full width */}
        <Route path="/" element={<Home />} />

        {/* App pages — WITH sidebar */}
        <Route element={<AppLayout />}>
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="analyzer" element={<Analyzer />} />
          <Route path="traffic" element={<Traffic />} />
          <Route path="rules" element={<Rules />} />
          <Route path="flows" element={<Flows />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
