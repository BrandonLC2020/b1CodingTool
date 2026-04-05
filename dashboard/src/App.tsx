import { useEffect, useState } from 'react'
import './index.css'

interface Module {
  name: string;
  status: string;
  path: string;
}

interface Config {
  upstream_repo: string;
  active_agents: string[];
}

function App() {
  const [view, setView] = useState<'modules' | 'context' | 'config' | 'telemetry'>('modules')
  const [project, setProject] = useState<{name: string, path: string} | null>(null)
  const [modules, setModules] = useState<Module[]>([])
  const [config, setConfig] = useState<Config | null>(null)
  const [context, setContext] = useState<string>('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [projRes, modRes, confRes, contRes] = await Promise.all([
          fetch('/api/project'),
          fetch('/api/modules'),
          fetch('/api/config'),
          fetch('/api/context')
        ])
        
        setProject(await projRes.json())
        setModules(await modRes.json())
        setConfig(await confRes.json())
        const contextData = await contRes.json()
        setContext(contextData.content)
      } catch (err) {
        console.error('Failed to fetch data:', err)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  if (loading) return <div style={{padding: '2rem'}}>Loading b1 Dashboard...</div>

  return (
    <div className="dashboard-container">
      <aside className="sidebar">
        <div className="logo">
          <span>\U0001f680</span> b1CodingTool
        </div>
        
        <nav style={{marginTop: '2rem'}}>
          <div className={`nav-item ${view === 'modules' ? 'active' : ''}`} onClick={() => setView('modules')}>
            \U0001f4e6 Modules
          </div>
          <div className={`nav-item ${view === 'context' ? 'active' : ''}`} onClick={() => setView('context')}>
            \U0001f4c4 Context Parity
          </div>
          <div className={`nav-item ${view === 'config' ? 'active' : ''}`} onClick={() => setView('config')}>
            \U0001f2d Settings
          </div>
          <div className={`nav-item ${view === 'telemetry' ? 'active' : ''}`} onClick={() => setView('telemetry')}>
            \U0001f4ca Telemetry
          </div>
        </nav>
        
        <div style={{marginTop: 'auto', fontSize: '0.8rem', color: 'var(--text-dim)'}}>
          Project: {project?.name}<br/>
          v0.1.0
        </div>
      </aside>

      <main className="main-content">
        <header className="header">
          <h1>{view.charAt(0).toUpperCase() + view.slice(1)}</h1>
          <p style={{color: 'var(--text-dim)'}}> Manage your agent lifecycle and guidelines. </p>
        </header>

        {view === 'modules' && (
          <section>
            <div className="header-actions" style={{display: 'flex', justifyContent: 'space-between', marginBottom: '2rem'}}>
              <h2>Installed Modules</h2>
              <button className="btn">+ Install Module</button>
            </div>
            <div className="card-grid">
              {modules.map(mod => (
                <div key={mod.name} className="card">
                  <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem'}}>
                    <h3 style={{margin: 0}}>{mod.name}</h3>
                    <span className="status-badge status-installed">Installed</span>
                  </div>
                  <p style={{fontSize: '0.9rem', color: 'var(--text-dim)'}}>Located at: {mod.path}</p>
                  <div style={{marginTop: '1.5rem', display: 'flex', gap: '0.5rem'}}>
                    <button className="btn" style={{backgroundColor: '#334155'}}>Update</button>
                    <button className="btn" style={{backgroundColor: '#ef4444', marginLeft: 'auto'}}>Uninstall</button>
                  </div>
                </div>
              ))}
              {modules.length === 0 && <p>No modules installed yet. Run <code>b1 install</code> to get started.</p>}
            </div>
          </section>
        )}

        {view === 'context' && (
          <section>
            <h2>Compiled Global Context</h2>
            <p style={{color: 'var(--text-dim)'}}>This is the unified context that fuels your agents (CLAUDE.md, GEMINI.md, etc.).</p>
            <div className="context-output">
              {context}
            </div>
            <button className="btn" style={{marginTop: '1.5rem'}}>Force Sync All Agents (b1 pair)</button>
          </section>
        )}

        {view === 'config' && (
          <section>
            <div className="card" style={{maxWidth: '600px'}}>
              <h2>Tracking Configuration</h2>
              <div style={{marginBottom: '1.5rem'}}>
                <label style={{display: 'block', marginBottom: '0.5rem'}}>Upstream Repository</label>
                <input 
                  type="text" 
                  value={config?.upstream_repo || ''} 
                  readOnly
                  style={{width: '100%', padding: '0.75rem', borderRadius: '6px', border: '1px solid var(--border-color)', backgroundColor: '#0f172a', color: 'white'}}
                />
              </div>
              <div style={{marginBottom: '1.5rem'}}>
                <label style={{display: 'block', marginBottom: '0.5rem'}}>Active Agent Parity</label>
                <div style={{display: 'flex', gap: '0.5rem'}}>
                  {config?.active_agents.map(agent => (
                    <span key={agent} className="status-badge" style={{backgroundColor: 'var(--accent-color)', padding: '0.5rem 0.75rem'}}>
                      {agent}
                    </span>
                  ))}
                </div>
              </div>
              <button className="btn">Edit Configuration</button>
            </div>
          </section>
        )}

        {view === 'telemetry' && (
          <section>
            <div className="card" style={{padding: '3rem', textAlign: 'center'}}>
              <h2 style={{color: 'var(--text-dim)'}}>Telemetry Processing</h2>
              <p>Real-time token monitoring and session tracking integration coming soon.</p>
              <div style={{marginTop: '2rem', height: '10px', width: '100%', backgroundColor: '#334155', borderRadius: '5px', overflow: 'hidden'}}>
                <div style={{height: '100%', width: '45%', backgroundColor: 'var(--accent-color)'}}></div>
              </div>
              <p style={{marginTop: '1rem', fontSize: '0.8rem', color: 'var(--text-dim)'}}>45% of Phase 5 Mock logic implemented</p>
            </div>
          </section>
        )}
      </main>
    </div>
  )
}

export default App
