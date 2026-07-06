import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, UploadCloud, FileText, CheckCircle, Clock, Zap, Settings, BookOpen } from 'lucide-react';
import apiClient from '../api/axios';

// UI Components
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Textarea } from '../components/ui/textarea';
import { Progress } from '../components/ui/progress';

const ProjectDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('knowledge'); // knowledge, generate, slides
  const [documents, setDocuments] = useState([]);
  const [uploading, setUploading] = useState(false);
  
  const [prompt, setPrompt] = useState('');
  const [generating, setGenerating] = useState(false);
  const [generationProgress, setGenerationProgress] = useState(0);
  const [generationProgressText, setGenerationProgressText] = useState("");
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
    setGenerationProgress(5);
    setGenerationProgressText("Initializing Request...");
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
        
        if (statusData.progress) setGenerationProgress(statusData.progress);
        if (statusData.progress_text) setGenerationProgressText(statusData.progress_text);
        
        if (statusData.status === "completed") {
          setGenerationProgress(100);
          setGenerationProgressText("Completed!");
          await new Promise(resolve => setTimeout(resolve, 500)); // Let the bar fill
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
      setGenerationProgress(0);
    }
  };

  return (
    <div className="space-y-6 h-[calc(100vh-6rem)] flex flex-col pt-6 pb-2 px-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button 
          variant="ghost" 
          size="icon"
          onClick={() => navigate('/projects')}
        >
          <ArrowLeft size={20} />
        </Button>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Project Workspace</h1>
          <p className="text-muted-foreground mt-1">Upload knowledge and let AI forge your slides.</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 p-1 bg-black/40 backdrop-blur-md rounded-xl w-max shadow-sm border border-white/10">
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
              className={`flex items-center gap-2 px-6 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isActive 
                  ? 'bg-primary/20 text-primary border border-primary/50 shadow-[0_0_15px_rgba(139,92,246,0.3)]' 
                  : 'text-muted-foreground hover:text-foreground hover:bg-white/5'
              }`}
            >
              <Icon size={16} />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Content Area */}
      <div className="flex-1 relative pb-6">
        <AnimatePresence mode="wait">
          {/* Knowledge Base Tab */}
          {activeTab === 'knowledge' && (
            <motion.div 
              key="knowledge"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3 }}
              className="h-full flex gap-6"
            >
              {/* Upload Area */}
              <div className="flex-1 flex flex-col h-full">
                <div 
                  {...getRootProps()} 
                  className={`flex-1 rounded-2xl border-2 border-dashed bg-black/20 backdrop-blur-sm flex flex-col items-center justify-center p-12 text-center cursor-pointer transition-all ${
                    isDragActive ? 'border-primary bg-primary/10 shadow-[0_0_30px_rgba(139,92,246,0.3)]' : 'border-white/20 hover:border-primary/50 hover:bg-white/5'
                  }`}
                >
                  <input {...getInputProps()} />
                  <div className={`w-24 h-24 rounded-full flex items-center justify-center mb-6 transition-all duration-500 ${
                    isDragActive ? 'bg-primary/20 text-primary scale-110 shadow-[0_0_30px_rgba(139,92,246,0.5)]' : 'bg-white/10 text-muted-foreground'
                  }`}>
                    <UploadCloud size={48} />
                  </div>
                  <h3 className="text-2xl font-semibold mb-2">
                    {isDragActive ? "Drop PDF to upload" : "Feed the AI Knowledge"}
                  </h3>
                  <p className="text-muted-foreground max-w-sm">
                    Drag & drop your source documents here. The AI will chunk, embed, and store them in the vector database.
                  </p>
                  {uploading && (
                    <div className="mt-8 flex items-center gap-3 text-primary font-medium bg-primary/10 px-6 py-3 rounded-full border border-primary/20">
                      <div className="w-5 h-5 border-2 border-primary/30 border-t-primary rounded-full animate-spin"></div>
                      Uploading & Processing...
                    </div>
                  )}
                </div>
              </div>

              {/* Document List */}
              <Card className="w-1/3 flex flex-col h-full bg-black/60 backdrop-blur-xl border-white/10">
                <CardHeader className="pb-4">
                  <CardTitle className="text-xl flex items-center gap-2">
                    <FileText size={20} className="text-primary" />
                    Neural Index
                  </CardTitle>
                  <CardDescription>Documents embedded in the vector store.</CardDescription>
                </CardHeader>
                <CardContent className="flex-1 overflow-y-auto">
                  {documents.length === 0 ? (
                    <div className="text-center p-8 bg-white/5 rounded-xl border border-dashed border-white/10">
                      <p className="text-sm text-muted-foreground">The index is empty.</p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {documents.map((doc) => (
                        <div key={doc.id} className="p-4 bg-white/5 rounded-xl border border-white/10 flex items-start gap-3 hover:bg-white/10 transition-all cursor-default">
                          <div className="mt-0.5 text-primary">
                            {doc.status === 'ready' ? (
                              <CheckCircle size={18} className="text-green-500" />
                            ) : (
                              <div className="relative">
                                <Clock size={18} className="text-amber-500 opacity-50" />
                                <div className="absolute inset-0 border-2 border-amber-500 rounded-full border-t-transparent animate-spin"></div>
                              </div>
                            )}
                          </div>
                          <div className="flex-1 overflow-hidden">
                            <p className="text-sm font-medium truncate" title={doc.filename}>{doc.filename}</p>
                            <div className="flex justify-between items-center mt-2">
                              <span className={`text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-full font-bold ${
                                doc.status === 'ready' ? 'bg-green-500/20 text-green-400 border border-green-500/30' : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                              }`}>
                                {doc.status || 'PROCESSING'}
                              </span>
                              <span className="text-xs font-mono text-muted-foreground">
                                {doc.total_chunks || 0} vectors
                              </span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          )}

          {/* Generate Tab */}
          {activeTab === 'generate' && (
            <motion.div 
              key="generate"
              initial={{ opacity: 0, scale: 0.98 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.98 }}
              transition={{ duration: 0.4 }}
              className="h-full flex flex-col items-center justify-center relative"
            >
              {/* Decorative background glow */}
              <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-3/4 h-3/4 bg-primary/20 blur-[120px] rounded-full pointer-events-none -z-10"></div>
              
              <Card className="max-w-3xl w-full border-white/10 shadow-[0_0_50px_rgba(0,0,0,0.5)] overflow-hidden">
                <div className="h-2 w-full bg-gradient-to-r from-primary/20 via-primary to-primary/20"></div>
                <CardHeader className="pt-8">
                  <CardTitle className="text-3xl text-center">Synthesize Presentation</CardTitle>
                  <CardDescription className="text-center text-base mt-2">
                    Describe your vision. The AI will weave it with knowledge from your index.
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6 pb-8">
                  <div className="relative">
                    <Textarea
                      value={prompt}
                      onChange={(e) => setPrompt(e.target.value)}
                      placeholder="e.g. Create a 10-slide pitch deck highlighting the key metrics from the uploaded Q3 report..."
                      className="min-h-[160px] text-lg p-5 leading-relaxed bg-black/40 border-white/20 focus-visible:ring-primary/50"
                    />
                    
                    {generating && (
                      <div className="absolute inset-0 bg-black/80 backdrop-blur-sm rounded-md flex flex-col items-center justify-center border border-primary/30 z-10 p-8">
                        <div className="relative w-20 h-20 mb-6">
                          <div className="absolute inset-0 border-4 border-primary/20 rounded-full"></div>
                          <div className="absolute inset-0 border-4 border-t-primary border-r-primary border-b-transparent border-l-transparent rounded-full animate-spin"></div>
                          <Zap className="absolute inset-0 m-auto text-primary animate-pulse" size={32} />
                        </div>
                        <h3 className="text-xl font-bold mb-2">Neural Engine Engaged</h3>
                        <p className="text-muted-foreground text-sm mb-6">{generationProgressText || "Connecting to neural network..."}</p>
                        <Progress value={generationProgress} className="w-full max-w-md h-2" />
                      </div>
                    )}
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <Button variant="ghost" className="text-muted-foreground hover:text-foreground">
                      <Settings className="mr-2" size={16} /> Advanced Parameters
                    </Button>
                    
                    <Button 
                      size="lg"
                      onClick={handleGenerate}
                      disabled={generating || !prompt.trim()}
                      className="text-base px-8 h-12"
                    >
                      <Zap className="mr-2" size={20} /> Ignite Generation
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}

          {/* Slides Tab */}
          {activeTab === 'slides' && (
            <motion.div 
              key="slides"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.4 }}
              className="h-full flex items-center justify-center"
            >
              <Card className="max-w-2xl w-full text-center p-12 border-white/10 bg-black/40">
                {presentationUrl ? (
                  <div className="flex flex-col items-center space-y-6">
                    <div className="relative">
                      <div className="absolute inset-0 bg-green-500/20 rounded-full blur-xl animate-pulse"></div>
                      <div className="w-24 h-24 bg-green-500/10 rounded-full flex items-center justify-center border border-green-500/30 relative z-10">
                        <CheckCircle size={48} className="text-green-400" />
                      </div>
                    </div>
                    <div>
                      <h2 className="text-3xl font-bold mb-3">Synthesis Complete</h2>
                      <p className="text-muted-foreground text-lg max-w-md mx-auto">Your presentation has been materialized and is ready for download.</p>
                    </div>
                    <Button 
                      size="lg"
                      className="h-14 px-10 text-lg w-full max-w-sm mt-4 bg-white text-black hover:bg-gray-200 shadow-[0_0_30px_rgba(255,255,255,0.3)]"
                      onClick={() => window.open(presentationUrl, '_blank')}
                    >
                      <FileText className="mr-3" size={24} /> Download Presentation
                    </Button>
                    <Button variant="ghost" onClick={() => setActiveTab('generate')} className="mt-2 text-muted-foreground">
                      Generate Another
                    </Button>
                  </div>
                ) : (
                  <div className="flex flex-col items-center space-y-6">
                    <div className="w-24 h-24 bg-white/5 rounded-full flex items-center justify-center border border-white/10">
                      <FileText size={48} className="text-muted-foreground" />
                    </div>
                    <div>
                      <h2 className="text-2xl font-bold mb-2">Awaiting Instructions</h2>
                      <p className="text-muted-foreground max-w-md mx-auto">No presentation exists for this project yet. Provide a prompt to begin synthesis.</p>
                    </div>
                    <Button onClick={() => setActiveTab('generate')} variant="outline" className="mt-4">
                      <Zap className="mr-2" size={16} /> Enter Generator
                    </Button>
                  </div>
                )}
              </Card>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default ProjectDetail;
