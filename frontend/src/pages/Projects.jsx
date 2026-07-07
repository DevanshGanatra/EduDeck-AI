import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Plus, FolderOpen, MoreVertical, Search, ArrowRight } from 'lucide-react';
import apiClient from '../api/axios';

const Projects = () => {
  const navigate = useNavigate();
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      const res = await apiClient.get('/projects/');
      // res.data.data will contain the PaginatedResponse
      setProjects(res.data.data.items || []);
    } catch (err) {
      console.error("Failed to fetch projects", err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProject = async (e) => {
    e.preventDefault();
    setCreating(true);
    try {
      const res = await apiClient.post('/projects/', {
        title: newTitle,
        description: newDesc
      });
      setProjects([res.data.data, ...projects]);
      setIsModalOpen(false);
      setNewTitle('');
      setNewDesc('');
    } catch (err) {
      console.error("Failed to create project", err);
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Section */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Your Workspaces</h1>
          <p className="text-muted-foreground text-sm mt-1">Manage your AI presentation projects</p>
        </div>
        
        <button 
          onClick={() => setIsModalOpen(true)}
          className="btn-primary flex items-center gap-2 shadow-brand-500/20 shadow-lg"
        >
          <Plus size={18} />
          New Project
        </button>
      </div>

      <div className="glass-panel p-3 flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" size={18} />
          <input 
            type="text" 
            placeholder="Search projects..." 
            className="w-full bg-transparent border-none focus:ring-0 pl-10 py-1 text-sm text-foreground placeholder-muted-foreground outline-none"
          />
        </div>
      </div>

      {/* Projects Grid */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="w-8 h-8 border-4 border-brand-200 border-t-brand-500 rounded-full animate-spin"></div>
        </div>
      ) : projects.length === 0 ? (
        <div className="glass-panel p-12 text-center flex flex-col items-center">
          <div className="w-16 h-16 bg-white/5 rounded-2xl flex items-center justify-center mb-4 border border-white/10">
            <FolderOpen size={32} className="text-muted-foreground" />
          </div>
          <h3 className="text-lg font-semibold text-foreground">No projects yet</h3>
          <p className="text-muted-foreground text-sm max-w-sm mt-2 mb-6">
            Create your first workspace to start uploading documents and generating AI presentations.
          </p>
          <button onClick={() => setIsModalOpen(true)} className="btn-secondary">
            Create First Project
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((project, index) => (
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              key={project.id}
              onClick={() => navigate(`/projects/${project.id}`)}
              className="glass-panel p-5 hover:border-primary/50 hover:shadow-xl hover:shadow-primary/20 transition-all group cursor-pointer flex flex-col h-full"
            >
              <div className="flex justify-between items-start mb-4">
                <div className="w-10 h-10 rounded-xl bg-primary/20 flex items-center justify-center text-primary font-bold text-lg border border-primary/30">
                  {project.title.charAt(0).toUpperCase()}
                </div>
                <button className="text-muted-foreground hover:text-foreground p-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <MoreVertical size={18} />
                </button>
              </div>
              <h3 className="font-semibold text-foreground text-lg mb-1 line-clamp-1">{project.title}</h3>
              <p className="text-muted-foreground text-sm line-clamp-2 mb-4 flex-1">
                {project.description || "No description provided."}
              </p>
              
              <div className="pt-4 border-t border-white/10 flex justify-between items-center mt-auto">
                <span className="text-xs font-medium text-muted-foreground bg-white/5 border border-white/10 px-2 py-1 rounded-md">
                  {project.document_count || 0} Documents
                </span>
                <div className="text-primary text-sm font-medium flex items-center gap-1 group-hover:gap-2 transition-all">
                  Open <ArrowRight size={14} />
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {/* Create Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="glass-panel max-w-md w-full overflow-hidden"
          >
            <div className="px-6 py-4 border-b border-white/10 flex justify-between items-center">
              <h3 className="font-bold text-foreground">Create New Project</h3>
              <button onClick={() => setIsModalOpen(false)} className="text-muted-foreground hover:text-foreground text-2xl leading-none">&times;</button>
            </div>
            
            <form onSubmit={handleCreateProject} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-foreground mb-1">Project Title</label>
                <input 
                  type="text" 
                  required
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  className="input-field"
                  placeholder="e.g. Q3 Marketing Plan"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-foreground mb-1">Description (Optional)</label>
                <textarea 
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  className="input-field min-h-[100px] resize-none"
                  placeholder="What is this presentation about?"
                />
              </div>
              
              <div className="pt-2 flex gap-3">
                <button type="button" onClick={() => setIsModalOpen(false)} className="flex-1 btn-secondary py-2.5">
                  Cancel
                </button>
                <button type="submit" disabled={creating} className="flex-1 btn-primary py-2.5">
                  {creating ? 'Creating...' : 'Create Project'}
                </button>
              </div>
            </form>
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default Projects;
