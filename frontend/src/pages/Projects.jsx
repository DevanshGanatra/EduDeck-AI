import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, FolderOpen, MoreVertical, Search, ArrowRight, Layers, X } from 'lucide-react';
import apiClient from '../api/axios';
import { useAuth } from '../context/AuthContext';

const Projects = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [creating, setCreating] = useState(false);

  useEffect(() => { fetchProjects(); }, []);

  const fetchProjects = async () => {
    try {
      const res = await apiClient.get('/projects/');
      setProjects(res.data.data.items || []);
    } catch (err) {
      console.error('Failed to fetch projects', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProject = async (e) => {
    e.preventDefault();
    setCreating(true);
    try {
      const res = await apiClient.post('/projects/', { title: newTitle, description: newDesc });
      setProjects([res.data.data, ...projects]);
      setIsModalOpen(false);
      setNewTitle('');
      setNewDesc('');
    } catch (err) {
      console.error('Failed to create project', err);
    } finally {
      setCreating(false);
    }
  };

  const filtered = projects.filter(p =>
    p.title.toLowerCase().includes(search.toLowerCase()) ||
    (p.description || '').toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-7 pb-8">

      {/* ── Header ── */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gradient">
            {user?.name ? `Hello, ${user.name.split(' ')[0]} 👋` : 'Your Workspaces'}
          </h1>
          <p className="text-muted-foreground text-sm mt-1">
            {projects.length} project{projects.length !== 1 ? 's' : ''} — AI presentation generation
          </p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="btn-primary shrink-0"
        >
          <Plus size={17} />
          New Project
        </button>
      </div>

      {/* ── Search bar ── */}
      <div className="glass flex items-center gap-3 px-4 py-2.5">
        <Search size={16} className="text-muted-foreground shrink-0" />
        <input
          type="text"
          value={search}
          onChange={e => setSearch(e.target.value)}
          placeholder="Search projects…"
          className="flex-1 bg-transparent text-sm text-foreground placeholder:text-muted-foreground outline-none"
        />
        {search && (
          <button onClick={() => setSearch('')} className="text-muted-foreground hover:text-foreground">
            <X size={14} />
          </button>
        )}
      </div>

      {/* ── Grid ── */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="glass rounded-2xl h-44 animate-pulse bg-white/3" />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass flex flex-col items-center justify-center py-24 text-center"
        >
          <div className="w-16 h-16 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center mb-4">
            <FolderOpen size={32} className="text-muted-foreground" />
          </div>
          <h3 className="text-lg font-semibold text-foreground">
            {search ? 'No matching projects' : 'No projects yet'}
          </h3>
          <p className="text-muted-foreground text-sm max-w-sm mt-2 mb-6">
            {search
              ? 'Try a different search term.'
              : 'Create your first workspace to start uploading documents and generating AI presentations.'}
          </p>
          {!search && (
            <button onClick={() => setIsModalOpen(true)} className="btn-secondary">
              Create First Project
            </button>
          )}
        </motion.div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filtered.map((project, i) => (
            <motion.div
              key={project.id}
              initial={{ opacity: 0, y: 18 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.06, duration: 0.35 }}
              onClick={() => navigate(`/projects/${project.id}`)}
              className="glass-hover p-5 cursor-pointer group flex flex-col min-h-[176px]"
            >
              {/* Card header */}
              <div className="flex items-start justify-between mb-4">
                <div className="w-11 h-11 rounded-xl bg-primary/15 border border-primary/25 flex items-center justify-center text-primary font-bold text-lg shrink-0">
                  {project.title.charAt(0).toUpperCase()}
                </div>
                <button
                  onClick={e => e.stopPropagation()}
                  className="p-1.5 text-muted-foreground hover:text-foreground opacity-0 group-hover:opacity-100 transition-all rounded-lg hover:bg-white/8"
                >
                  <MoreVertical size={16} />
                </button>
              </div>

              {/* Title & description */}
              <h3 className="font-semibold text-foreground text-base mb-1 line-clamp-1">{project.title}</h3>
              <p className="text-muted-foreground text-sm line-clamp-2 flex-1">
                {project.description || 'No description provided.'}
              </p>

              {/* Footer */}
              <div className="flex items-center justify-between mt-4 pt-4 border-t border-white/8">
                <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                  <Layers size={12} />
                  {project.document_count ?? 0} docs
                </div>
                <span className="flex items-center gap-1 text-xs font-semibold text-primary opacity-0 group-hover:opacity-100 transition-all -translate-x-2 group-hover:translate-x-0">
                  Open <ArrowRight size={13} />
                </span>
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {/* ── Create Modal ── */}
      <AnimatePresence>
        {isModalOpen && (
          <motion.div
            key="modal-backdrop"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
            onClick={() => setIsModalOpen(false)}
          >
            <motion.div
              key="modal"
              initial={{ opacity: 0, scale: 0.94, y: 16 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.94, y: 16 }}
              transition={{ duration: 0.25, ease: 'easeOut' }}
              className="glass w-full max-w-md overflow-hidden shadow-[0_32px_80px_rgba(0,0,0,0.6)]"
              onClick={e => e.stopPropagation()}
            >
              {/* Top accent */}
              <div className="h-px w-full bg-gradient-to-r from-transparent via-primary/60 to-transparent" />

              <div className="px-6 pt-6 pb-4 flex items-center justify-between">
                <h3 className="font-bold text-foreground text-lg">Create New Project</h3>
                <button
                  onClick={() => setIsModalOpen(false)}
                  className="text-muted-foreground hover:text-foreground transition-colors p-1.5 rounded-lg hover:bg-white/8"
                >
                  <X size={18} />
                </button>
              </div>

              <form onSubmit={handleCreateProject} className="px-6 pb-6 space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1.5">
                    Project Title *
                  </label>
                  <input
                    type="text"
                    required
                    value={newTitle}
                    onChange={e => setNewTitle(e.target.value)}
                    className="input-field w-full"
                    placeholder="e.g. Q3 Marketing Strategy"
                    autoFocus
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1.5">
                    Description
                  </label>
                  <textarea
                    value={newDesc}
                    onChange={e => setNewDesc(e.target.value)}
                    className="input-field w-full min-h-[90px] resize-none"
                    placeholder="What is this presentation about?"
                  />
                </div>

                <div className="flex gap-3 pt-2">
                  <button
                    type="button"
                    onClick={() => setIsModalOpen(false)}
                    className="btn-secondary flex-1"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={creating || !newTitle.trim()}
                    className="btn-primary flex-1"
                  >
                    {creating ? (
                      <>
                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        Creating…
                      </>
                    ) : (
                      <>
                        <Plus size={16} /> Create Project
                      </>
                    )}
                  </button>
                </div>
              </form>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default Projects;
