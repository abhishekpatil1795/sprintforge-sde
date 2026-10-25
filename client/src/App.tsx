import { FormEvent, useEffect, useMemo, useState } from 'react';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
type User = { id: number; name: string; email: string };
type Project = { id: number; name: string; description: string; updated_at: string; task_count: number; owner_id: number };
type Task = { id: number; title: string; description: string; status: 'TODO' | 'IN_PROGRESS' | 'DONE'; priority: 'LOW' | 'MEDIUM' | 'HIGH'; due_date?: string | null };

async function api<T>(path: string, token: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API}${path}`, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}), ...options.headers }
  });
  if (response.status === 204) return undefined as T;
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.detail || body.error || `Request failed (${response.status})`);
  return body as T;
}

export default function App() {
  const [token, setToken] = useState(() => localStorage.getItem('sf-token') || '');
  const [user, setUser] = useState<User | null>(null);
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [projects, setProjects] = useState<Project[]>([]);
  const [selected, setSelected] = useState<Project | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const [projectName, setProjectName] = useState('');
  const [projectDescription, setProjectDescription] = useState('');
  const [taskTitle, setTaskTitle] = useState('');
  const [taskDescription, setTaskDescription] = useState('');
  const [taskPriority, setTaskPriority] = useState<'LOW' | 'MEDIUM' | 'HIGH'>('MEDIUM');
  const [filter, setFilter] = useState<'ALL' | Task['status']>('ALL');

  async function loadProjects(authToken = token) {
    const result = await api<Project[]>('/projects', authToken);
    setProjects(result);
    if (selected) {
      const fresh = result.find(p => p.id === selected.id);
      if (fresh) setSelected(fresh);
    }
  }
  async function loadTasks(project = selected, authToken = token) {
    if (!project) { setTasks([]); return; }
    const result = await api<{ tasks: Task[]; pagination: { page: number; limit: number; total: number; pages: number } }>(`/projects/${project.id}/tasks?limit=100`, authToken);
    setTasks(result.tasks);
  }

  useEffect(() => {
    if (!token) return;
    api<User>('/auth/me', token).then(setUser).catch(() => {
      localStorage.removeItem('sf-token'); setToken(''); setUser(null);
    });
  }, [token]);

  useEffect(() => {
    if (!token || !user) return;
    loadProjects().catch(e => setError(e.message));
  }, [token, user]);

  useEffect(() => {
    if (selected && token) loadTasks(selected).catch(e => setError(e.message));
  }, [selected?.id, token]);

  const visibleTasks = useMemo(() => filter === 'ALL' ? tasks : tasks.filter(t => t.status === filter), [tasks, filter]);
  const counts = useMemo(() => ({
    total: tasks.length,
    todo: tasks.filter(t => t.status === 'TODO').length,
    active: tasks.filter(t => t.status === 'IN_PROGRESS').length,
    done: tasks.filter(t => t.status === 'DONE').length
  }), [tasks]);

  async function authenticate(e: FormEvent<HTMLFormElement>) {
    e.preventDefault(); setBusy(true); setError('');
    const form = new FormData(e.currentTarget);
    const payload: Record<string, string> = {
      email: String(form.get('email')), password: String(form.get('password'))
    };
    if (mode === 'register') payload.name = String(form.get('name'));
    try {
      const result = await api<{ token: string; user: User }>(`/auth/${mode === 'register' ? 'register' : 'login'}`, '', {
        method: 'POST', body: JSON.stringify(payload)
      });
      localStorage.setItem('sf-token', result.token);
      setUser(result.user); setToken(result.token);
    } catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }

  async function createProject(e: FormEvent) {
    e.preventDefault(); setError('');
    try {
      const result = await api<Project>('/projects', token, {
        method: 'POST', body: JSON.stringify({ name: projectName, description: projectDescription })
      });
      setProjects(current => [result, ...current]);
      setSelected(result); setProjectName(''); setProjectDescription('');
    } catch (e) { setError((e as Error).message); }
  }

  async function createTask(e: FormEvent) {
    e.preventDefault();
    if (!selected) return;
    setError('');
    try {
      await api(`/projects/${selected.id}/tasks`, token, {
        method: 'POST', body: JSON.stringify({ title: taskTitle, description: taskDescription, priority: taskPriority })
      });
      setTaskTitle(''); setTaskDescription(''); await loadTasks(selected); await loadProjects();
    } catch (e) { setError((e as Error).message); }
  }

  async function updateTask(task: Task, patch: Partial<Task>) {
    setError('');
    try {
      await api(`/tasks/${task.id}`, token, { method: 'PATCH', body: JSON.stringify(patch) });
      await loadTasks(selected); await loadProjects();
    } catch (e) { setError((e as Error).message); }
  }

  async function deleteTask(task: Task) {
    if (!confirm(`Delete "${task.title}"?`)) return;
    try {
      await api(`/tasks/${task.id}`, token, { method: 'DELETE' });
      await loadTasks(selected); await loadProjects();
    } catch (e) { setError((e as Error).message); }
  }

  function logout() {
    localStorage.removeItem('sf-token'); setToken(''); setUser(null); setProjects([]); setSelected(null); setTasks([]);
  }

  if (!token || !user) return (
    <main className="auth-page">
      <section className="auth-card">
        <div className="brand-mark">SF</div>
        <p className="eyebrow">TEAM WORKSPACE</p>
        <h1>Make work <span>flow.</span></h1>
        <p className="muted">A clear view of projects, tasks, and momentum.</p>
        <div className="tabs">
          <button className={mode === 'login' ? 'tab active' : 'tab'} onClick={() => setMode('login')}>Sign in</button>
          <button className={mode === 'register' ? 'tab active' : 'tab'} onClick={() => setMode('register')}>Create account</button>
        </div>
        <form onSubmit={authenticate} className="form-stack">
          {mode === 'register' && <label>Full name<input name="name" placeholder="Alex Morgan" minLength={2} required /></label>}
          <label>Email address<input name="email" type="email" placeholder="you@example.com" required /></label>
          <label>Password<input name="password" type="password" minLength={8} placeholder="At least 8 characters" required /></label>
          {error && <div className="alert">{error}</div>}
          <button className="primary full" disabled={busy}>{busy ? 'Please wait…' : mode === 'register' ? 'Create workspace account' : 'Sign in to workspace'}</button>
        </form>
        <p className="footnote">Built for teams that ship thoughtful work.</p>
      </section>
    </main>
  );

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><div className="brand-mark small">SF</div><span>SprintForge</span></div>
        <p className="nav-label">WORKSPACE</p>
        <button className="nav-item active"><span>▦</span> Projects <span className="nav-count">{projects.length}</span></button>
        <div className="side-section">
          <div className="section-head"><span className="nav-label">YOUR PROJECTS</span><span>{projects.length}</span></div>
          {projects.map(p => <button key={p.id} className={`project-link ${selected?.id === p.id ? 'chosen' : ''}`} onClick={() => setSelected(p)}><span className="project-dot">{p.name.slice(0, 1).toUpperCase()}</span><span className="project-name">{p.name}</span></button>)}
          {!projects.length && <p className="side-empty">Create a project to get started.</p>}
        </div>
        <div className="sidebar-bottom"><div className="avatar">{user.name.slice(0, 1).toUpperCase()}</div><div className="user-meta"><strong>{user.name}</strong><small>{user.email}</small></div><button className="logout" onClick={logout} title="Sign out">↗</button></div>
      </aside>

      <main className="main-content">
        <header className="topbar"><div><span className="crumb">Workspace</span><span className="slash">/</span><strong>{selected?.name || 'Projects'}</strong></div><div className="topbar-right"><span className="status-dot"></span><span>Workspace online</span><div className="avatar mini">{user.name.slice(0, 1).toUpperCase()}</div></div></header>
        <div className="content-wrap">
          {error && <div className="alert inline-alert">{error}<button onClick={() => setError('')}>Dismiss</button></div>}
          {!selected ? (
            <>
              <div className="page-heading"><div><p className="eyebrow">OVERVIEW</p><h1>Your projects</h1><p className="muted">Create a focused space for your team's next delivery.</p></div></div>
              <section className="panel create-panel"><div><p className="eyebrow">NEW WORKSPACE</p><h2>Start a project</h2><p className="muted">Projects keep related tasks and progress in one place.</p></div><form className="create-form" onSubmit={createProject}><input value={projectName} onChange={e => setProjectName(e.target.value)} placeholder="Project name" minLength={2} required /><input value={projectDescription} onChange={e => setProjectDescription(e.target.value)} placeholder="Short description (optional)" /><button className="primary">+ Create project</button></form></section>
              <div className="section-title"><h2>All projects</h2><span>{projects.length} total</span></div>
              <div className="project-grid">{projects.map(p => <button key={p.id} className="project-card" onClick={() => setSelected(p)}><div className="card-top"><div className="project-icon">{p.name.slice(0, 1).toUpperCase()}</div><span className="arrow">↗</span></div><h3>{p.name}</h3><p>{p.description || 'No description added yet.'}</p><div className="card-bottom"><span>{p.task_count} tasks</span><span>Open project →</span></div></button>)}</div>
            </>
          ) : (
            <>
              <div className="page-heading project-heading"><div><button className="back-link" onClick={() => setSelected(null)}>← All projects</button><p className="eyebrow">PROJECT WORKSPACE</p><h1>{selected.name}</h1><p className="muted">{selected.description || 'Track tasks and move the work forward.'}</p></div><button className="secondary" onClick={() => { loadTasks(selected); loadProjects(); }}>↻ Refresh</button></div>
              <div className="stats-grid">
                <div className="stat-card"><span className="stat-icon violet">▦</span><span className="stat-label">Total tasks</span><strong>{counts.total}</strong><small>Across this project</small></div>
                <div className="stat-card"><span className="stat-icon amber">◷</span><span className="stat-label">To do</span><strong>{counts.todo}</strong><small>Ready to start</small></div>
                <div className="stat-card"><span className="stat-icon blue">↗</span><span className="stat-label">In progress</span><strong>{counts.active}</strong><small>Currently moving</small></div>
                <div className="stat-card"><span className="stat-icon green">✓</span><span className="stat-label">Completed</span><strong>{counts.done}</strong><small>Work shipped</small></div>
              </div>
              <section className="panel task-panel">
                <div className="task-panel-head"><div><p className="eyebrow">EXECUTION</p><h2>Task board</h2></div><span className="task-total">{tasks.length} tasks</span></div>
                <form className="task-create" onSubmit={createTask}><input value={taskTitle} onChange={e => setTaskTitle(e.target.value)} placeholder="What needs to get done?" minLength={2} required /><input value={taskDescription} onChange={e => setTaskDescription(e.target.value)} placeholder="Task description (optional)" /><select value={taskPriority} onChange={e => setTaskPriority(e.target.value as typeof taskPriority)}><option value="LOW">Low priority</option><option value="MEDIUM">Medium priority</option><option value="HIGH">High priority</option></select><button className="primary">+ Add task</button></form>
                <div className="filters"><span className="nav-label">FILTER BY STATUS</span><div>{(['ALL', 'TODO', 'IN_PROGRESS', 'DONE'] as const).map(f => <button key={f} className={filter === f ? 'filter active' : 'filter'} onClick={() => setFilter(f)}>{f === 'ALL' ? 'All tasks' : f === 'TODO' ? 'To do' : f === 'IN_PROGRESS' ? 'In progress' : 'Done'}</button>)}</div></div>
                <div className="task-list">{visibleTasks.map(task => <article className="task-row" key={task.id}><button className={`check ${task.status === 'DONE' ? 'checked' : ''}`} onClick={() => updateTask(task, { status: task.status === 'DONE' ? 'TODO' : 'DONE' })} title="Toggle completion">{task.status === 'DONE' ? '✓' : ''}</button><div className="task-info"><strong className={task.status === 'DONE' ? 'completed-title' : ''}>{task.title}</strong><span>{task.description || 'No description'} · Updated task</span></div><span className={`priority ${task.priority.toLowerCase()}`}>{task.priority}</span><select aria-label={`Status for ${task.title}`} className="status-select" value={task.status} onChange={e => updateTask(task, { status: e.target.value as Task['status'] })}><option value="TODO">To do</option><option value="IN_PROGRESS">In progress</option><option value="DONE">Done</option></select><button className="delete-task" onClick={() => deleteTask(task)} title="Delete task">×</button></article>)}
                {!visibleTasks.length && <div className="empty-state"><div className="empty-icon">✓</div><h3>{filter === 'ALL' ? 'Your board is clear' : 'No tasks in this view'}</h3><p>Add a task above or switch the status filter.</p></div>}</div>
              </section>
            </>
          )}
          <footer>SPRINTFORGE <span>·</span> Make progress visible.</footer>
        </div>
      </main>
    </div>
  );
}
