import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import { motion } from 'framer-motion';
import { ArrowLeft, UploadCloud, FileText, CheckCircle, Clock, Zap, Settings, BookOpen } from 'lucide-react';
import apiClient from '../api/axios';

const ProjectDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('knowledge'); // knowledge, generate, slides
  const [documents, setDocuments] = useState([]);
  const [uploading, setUploading] = useState(false);
  
  const [prompt, setPrompt] = useState('');
  const [generating, setGenerating] = useState(false);
  const [presentationUrl, setPresentationUrl] = useState(null);

  useEffect(() => {
    fetchDocuments();
    
    // Poll for document status
    const interval = setInterval(() => {
      setDocuments(currentDocs => {
        // Only fetch if there's a document still processing
        const needsPolling = currentDocs.some(d => d.status !== 'ready' && d.status !== 'failed');
        if (needsPolling) {
          fetchDocuments();
        }
        return currentDocs;
      });
    }, 3000);
    
    return () => clearInterval(interval);
  }, [id]);

  const fetchDocuments = async () => {
    try {
      const res = await apiClient.get(`/documents/project/${id}`);
      setDocuments(res.data.data || []);
    } catch (err) {
      console.error("Failed to fetch documents", err);
    }
  };

  const onDrop = useCallback(async (acceptedFiles) => {
    if (acceptedFiles.length === 0) return;
    
    setUploading(true);
    const file = acceptedFiles[0];
    const formData = new FormData();
    formData.append('file', file);
    formData.append('project_id', id);

    try {
      await apiClient.post('/documents/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      fetchDocuments();
    } catch (err) {
      console.error("Upload failed", err);
    } finally {
      setUploading(false);
    }
  }, [id]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    maxFiles: 1
  });

  const handleGenerate = async () => {
    if (!prompt.trim()) return;
    setGenerating(true);
    try {
      const res = await apiClient.post('/generation/generate', {
        project_id: id,
        prompt: prompt
      });
      
      const jobId = res.data.data.job_id;
      
      // Poll for status
      while (true) {
        await new Promise(resolve => setTimeout(resolve, 2000));
        const statusRes = await apiClient.get(`/generation/generate/status/${jobId}`);
        const statusData = statusRes.data.data;
        
        if (statusData.status === "completed") {
          setPresentationUrl(statusData.download_url);
          setActiveTab('slides');
          break;
        } else if (statusData.status === "failed") {
          console.error("Generation failed:", statusData.error_message);
          alert("Generation failed: " + statusData.error_message);
          break;
        }
      }
    } catch (err) {
      console.error("Generation failed", err);
      alert("Generation failed: " + (err.response?.data?.message || err.message));
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="space-y-6 h-[calc(100vh-6rem)] flex flex-col">
      {/* Header */}
      <div className="flex items-center gap-4">
        <button 
          onClick={() => navigate('/projects')}
          className="p-2 hover:bg-white/50 rounded-xl transition-colors text-gray-500 hover:text-gray-900"
        >
          <ArrowLeft size={20} />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Project Workspace</h1>
          <p className="text-gray-500 text-sm mt-1">Upload knowledge and generate presentations</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 p-1 bg-white/40 backdrop-blur-md rounded-xl w-max shadow-sm border border-white/50">
        {[
          { id: 'knowledge', label: 'Knowledge Base', icon: BookOpen },
          { id: 'generate', label: 'AI Generator', icon: Zap },
          { id: 'slides', label: 'Slides', icon: FileText }
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                isActive 
                  ? 'bg-white text-brand-600 shadow-sm shadow-brand-500/10' 
                  : 'text-gray-500 hover:text-gray-900 hover:bg-white/50'
              }`}
            >
              <Icon size={16} />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-hidden relative">
        {/* Knowledge Base Tab */}
        {activeTab === 'knowledge' && (
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="h-full flex gap-6"
          >
            {/* Upload Area */}
            <div className="flex-1 flex flex-col">
              <div 
                {...getRootProps()} 
                className={`flex-1 glass-panel border-2 border-dashed flex flex-col items-center justify-center p-12 text-center cursor-pointer transition-all ${
                  isDragActive ? 'border-brand-500 bg-brand-50/50' : 'border-gray-200 hover:border-brand-300 hover:bg-white/40'
                }`}
              >
                <input {...getInputProps()} />
                <div className={`w-20 h-20 rounded-full flex items-center justify-center mb-6 transition-colors ${
                  isDragActive ? 'bg-brand-100 text-brand-600' : 'bg-gray-100 text-gray-400'
                }`}>
                  <UploadCloud size={40} />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {isDragActive ? "Drop PDF here" : "Upload source document"}
                </h3>
                <p className="text-gray-500 max-w-sm">
                  Drag and drop a PDF file here, or click to select a file. The AI will read and chunk this document.
                </p>
                {uploading && (
                  <div className="mt-6 flex items-center gap-2 text-brand-600 font-medium bg-brand-50 px-4 py-2 rounded-full">
                    <div className="w-4 h-4 border-2 border-brand-200 border-t-brand-600 rounded-full animate-spin"></div>
                    Uploading...
                  </div>
                )}
              </div>
            </div>

            {/* Document List */}
            <div className="w-1/3 glass-panel p-5 overflow-y-auto">
              <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <FileText size={18} className="text-brand-500" />
                Processed Documents
              </h3>
              
              {documents.length === 0 ? (
                <div className="text-center p-6 bg-gray-50 rounded-xl border border-dashed border-gray-200">
                  <p className="text-sm text-gray-500">No documents uploaded yet.</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {documents.map((doc) => (
                    <div key={doc.id} className="p-3 bg-white/60 rounded-xl border border-white/80 shadow-sm flex items-start gap-3 hover:shadow-md transition-all">
                      <div className="mt-1 text-brand-500">
                        {doc.status === 'ready' ? <CheckCircle size={18} /> : <Clock size={18} className="animate-pulse text-amber-500" />}
                      </div>
                      <div className="flex-1 overflow-hidden">
                        <p className="text-sm font-medium text-gray-900 truncate">{doc.filename}</p>
                        <div className="flex justify-between items-center mt-1">
                          <span className={`text-xs px-2 py-0.5 rounded-md font-medium ${
                            doc.status === 'ready' ? 'bg-green-50 text-green-700' : 'bg-amber-50 text-amber-700'
                          }`}>
                            {doc.status ? doc.status.toUpperCase() : 'PROCESSING'}
                          </span>
                          <span className="text-xs text-gray-400">
                            {doc.total_chunks} chunks
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </motion.div>
        )}

        {/* Generate Tab */}
        {activeTab === 'generate' && (
          <motion.div 
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="h-full flex items-center justify-center"
          >
            <div className="max-w-3xl w-full">
              <div className="glass-panel p-8 relative overflow-hidden">
                <div className="absolute top-0 right-0 w-64 h-64 bg-brand-500/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2"></div>
                
                <h2 className="text-3xl font-bold text-gray-900 mb-2 relative z-10">What should the presentation be about?</h2>
                <p className="text-gray-500 mb-8 relative z-10">Describe the presentation you want to generate. The AI will pull relevant information from your Knowledge Base.</p>
                
                <div className="space-y-4 relative z-10">
                  <textarea
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    placeholder="e.g. Create a 10-slide pitch deck highlighting the key metrics from the uploaded Q3 report..."
                    className="w-full h-40 input-field text-lg resize-none p-4"
                  />
                  
                  <div className="flex justify-between items-center pt-2">
                    <button className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-900 px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors">
                      <Settings size={16} /> Advanced Options
                    </button>
                    
                    <button 
                      onClick={handleGenerate}
                      disabled={generating || !prompt.trim()}
                      className="btn-primary py-3 px-8 text-lg flex items-center gap-2 shadow-brand-500/30 shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {generating ? (
                        <>
                          <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                          Generating Magic...
                        </>
                      ) : (
                        <>
                          <Zap size={20} /> Generate Presentation
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {/* Slides Tab */}
        {activeTab === 'slides' && (
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="h-full"
          >
            <div className="glass-panel h-full p-8 flex flex-col items-center justify-center text-center">
              {presentationUrl ? (
                <>
                  <div className="w-24 h-24 bg-green-50 rounded-full flex items-center justify-center mb-6">
                    <CheckCircle size={48} className="text-green-500" />
                  </div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-2">Presentation Ready!</h2>
                  <p className="text-gray-500 mb-8 max-w-md">Your presentation has been generated successfully using AI and your knowledge base.</p>
                  <a 
                    href={presentationUrl} 
                    target="_blank" 
                    rel="noreferrer"
                    className="btn-primary py-3 px-8 text-lg flex items-center gap-2 shadow-brand-500/30 shadow-xl"
                  >
                    Download PPTX
                  </a>
                </>
              ) : (
                <>
                  <div className="w-24 h-24 bg-gray-50 rounded-full flex items-center justify-center mb-6">
                    <FileText size={48} className="text-gray-400" />
                  </div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-2">No Presentation Yet</h2>
                  <p className="text-gray-500 mb-8 max-w-md">Go to the AI Generator tab to create your first presentation.</p>
                  <button onClick={() => setActiveTab('generate')} className="btn-secondary">
                    Go to Generator
                  </button>
                </>
              )}
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default ProjectDetail;
