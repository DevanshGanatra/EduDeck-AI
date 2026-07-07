import React, { useState } from 'react';
import { useNavigate, Navigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Eye, EyeOff, AlertCircle, Sparkles, ArrowRight } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const FEATURES = [
  { icon: '🧠', text: 'AI-powered slide generation from your documents' },
  { icon: '⚡', text: 'Real-time vector search across your knowledge base' },
  { icon: '✏️', text: 'In-app editor before exporting to PPTX' },
];

const Login = () => {
  const [mode, setMode] = useState('login');
  const [email, setEmail] = useState('test@example.com');
  const [password, setPassword] = useState('Password123');
  const [name, setName] = useState('');
  const [showPass, setShowPass] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const { login, register, user } = useAuth();
  const navigate = useNavigate();

  if (user) return <Navigate to="/projects" replace />;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const result = mode === 'login'
      ? await login(email, password)
      : await register(email, password, name || undefined);

    if (result?.success) {
      navigate('/projects');
    } else {
      setError(result?.error || 'Something went wrong. Please try again.');
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-background flex overflow-hidden relative">

      {/* ─── Left panel (desktop only) ─── */}
      <div className="hidden lg:flex w-[45%] relative flex-col justify-between p-12 overflow-hidden">
        {/* Glow blobs */}
        <div className="absolute -top-40 -left-40 w-[500px] h-[500px] rounded-full"
             style={{ background: 'radial-gradient(circle, rgba(139,92,246,0.25) 0%, transparent 70%)' }} />
        <div className="absolute bottom-0 right-0 w-[400px] h-[400px] rounded-full"
             style={{ background: 'radial-gradient(circle, rgba(59,130,246,0.15) 0%, transparent 70%)' }} />

        {/* Logo */}
        <div className="flex items-center gap-3 relative z-10">
          <div className="w-10 h-10 rounded-xl flex items-center justify-center text-white font-bold text-xl"
               style={{ background: 'linear-gradient(135deg, #7c3aed, #6d28d9)', boxShadow: '0 0 24px rgba(139,92,246,0.5)' }}>
            E
          </div>
          <span className="text-xl font-bold text-gradient">EduDeck AI</span>
        </div>

        {/* Hero text */}
        <div className="space-y-8 relative z-10">
          <div>
            <h2 className="text-5xl font-bold leading-tight text-gradient mb-4">
              Turn documents<br />into decks — instantly.
            </h2>
            <p className="text-muted-foreground text-lg leading-relaxed">
              Upload your PDFs, feed the AI, and get a polished presentation in under a minute.
            </p>
          </div>

          {/* Feature list */}
          <div className="space-y-4">
            {FEATURES.map((f, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -16 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 + i * 0.12 }}
                className="flex items-center gap-3"
                style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: '12px', padding: '12px 16px' }}
              >
                <span className="text-2xl">{f.icon}</span>
                <span className="text-sm text-muted-foreground">{f.text}</span>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Bottom credit */}
        <p className="text-xs text-muted-foreground relative z-10">
          Powered by Gemini 2.5 Flash &amp; pgvector
        </p>
      </div>

      {/* Vertical divider */}
      <div className="hidden lg:block w-px my-12"
           style={{ background: 'linear-gradient(to bottom, transparent, rgba(255,255,255,0.1), transparent)' }} />

      {/* ─── Right panel — Auth form ─── */}
      <div className="flex-1 flex flex-col items-center justify-center px-6 py-12 relative">
        {/* Mobile logo */}
        <div className="flex lg:hidden items-center gap-3 mb-10">
          <div className="w-10 h-10 rounded-xl flex items-center justify-center text-white font-bold text-xl"
               style={{ background: 'linear-gradient(135deg, #7c3aed, #6d28d9)', boxShadow: '0 0 24px rgba(139,92,246,0.5)' }}>
            E
          </div>
          <span className="text-xl font-bold text-gradient">EduDeck AI</span>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="w-full max-w-sm"
        >
          {/* Heading */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-foreground mb-1.5">
              {mode === 'login' ? 'Welcome back' : 'Get started'}
            </h1>
            <p className="text-muted-foreground text-sm">
              {mode === 'login'
                ? 'Sign in to access your workspace.'
                : 'Create a free account — no credit card needed.'}
            </p>
          </div>

          {/* Error */}
          <AnimatePresence>
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                className="flex items-start gap-2.5 p-3 mb-5 rounded-xl text-sm text-red-400"
                style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.2)' }}
              >
                <AlertCircle size={15} className="mt-0.5 shrink-0" />
                {error}
              </motion.div>
            )}
          </AnimatePresence>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">

            <AnimatePresence>
              {mode === 'register' && (
                <motion.div
                  key="name"
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.2 }}
                >
                  <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-widest mb-2">
                    Full Name
                  </label>
                  <input
                    type="text"
                    value={name}
                    onChange={e => setName(e.target.value)}
                    className="input-field w-full"
                    placeholder="Your name"
                  />
                </motion.div>
              )}
            </AnimatePresence>

            {/* Email */}
            <div>
              <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-widest mb-2">
                Email address
              </label>
              <input
                type="email"
                required
                value={email}
                onChange={e => setEmail(e.target.value)}
                className="input-field w-full"
                placeholder="you@example.com"
              />
            </div>

            {/* Password */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-widest">
                  Password
                </label>
                {mode === 'login' && (
                  <button type="button" className="text-xs text-primary hover:underline">
                    Forgot password?
                  </button>
                )}
              </div>
              <div className="relative">
                <input
                  type={showPass ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  className="input-field w-full pr-11"
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  onClick={() => setShowPass(s => !s)}
                  className="absolute right-3.5 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                >
                  {showPass ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
              {mode === 'register' && (
                <p className="text-xs text-muted-foreground mt-1.5">
                  Minimum 8 characters, 1 uppercase letter, 1 number
                </p>
              )}
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full py-3 text-sm mt-2"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  {mode === 'login' ? 'Signing in…' : 'Creating account…'}
                </span>
              ) : (
                <span className="flex items-center justify-center gap-2">
                  {mode === 'register' ? <Sparkles size={16} /> : <ArrowRight size={16} />}
                  {mode === 'login' ? 'Sign in' : 'Create free account'}
                </span>
              )}
            </button>
          </form>

          {/* OR divider */}
          <div className="flex items-center gap-3 my-6">
            <div className="flex-1 h-px" style={{ background: 'rgba(255,255,255,0.08)' }} />
            <span className="text-xs text-muted-foreground">or</span>
            <div className="flex-1 h-px" style={{ background: 'rgba(255,255,255,0.08)' }} />
          </div>

          {/* Toggle */}
          <button
            onClick={() => { setMode(m => m === 'login' ? 'register' : 'login'); setError(null); }}
            className="w-full text-center text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            {mode === 'login'
              ? <>Don't have an account? <span className="text-primary font-semibold">Sign up free</span></>
              : <>Already have an account? <span className="text-primary font-semibold">Sign in</span></>}
          </button>
        </motion.div>

        {/* Footer */}
        <p className="absolute bottom-6 text-xs text-muted-foreground">
          By continuing you agree to our Terms &amp; Privacy Policy.
        </p>
      </div>
    </div>
  );
};

export default Login;
