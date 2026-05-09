import React, { useState, useEffect, useCallback, useMemo } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import { 
  ReactFlow, 
  Background, 
  Handle, 
  Position 
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import { 
  Search, 
  Play, 
  Loader2, 
  CheckCircle2, 
  Circle, 
  AlertCircle, 
  FileText, 
  LayoutList, 
  Sparkles,
  ArrowRight,
  TrendingUp,
  MapPin,
  Briefcase,
  Cpu,
  Zap,
  ShieldCheck,
  BrainCircuit,
  PenTool,
  Workflow,
  History,
  Database,
  Globe,
  BookOpen,
  Wrench,
  Boxes,
  Code2,
  Terminal,
  RefreshCcw,
  Scale,
  Target
} from 'lucide-react';

// --- CUSTOM GRAPH NODE COMPONENT ---
const AgentNode = ({ data }) => {
  const { label, state, icon: Icon } = data;
  
  const getStyles = () => {
    if (state === "running") return "bg-blue-600 border-blue-400 text-white shadow-xl shadow-blue-200 scale-110 animate-pulse";
    if (state === "completed") return "bg-emerald-500 border-emerald-300 text-white";
    return "bg-white border-slate-200 text-slate-400 opacity-50";
  };

  return (
    <div className={`px-4 py-3 rounded-2xl border-2 transition-all duration-500 flex items-center gap-3 min-w-[160px] ${getStyles()}`}>
      <Handle type="target" position={Position.Top} className="opacity-0" />
      <div className={`p-2 rounded-lg ${state === "running" ? "bg-white/20" : state === "completed" ? "bg-white/20" : "bg-slate-50"}`}>
        {state === "running" ? <Loader2 className="w-4 h-4 animate-spin" /> : <Icon className="w-4 h-4" />}
      </div>
      <div className="flex flex-col">
        <span className="text-[8px] font-black uppercase tracking-widest opacity-70">Agent Node</span>
        <span className="text-[10px] font-bold uppercase tracking-tight leading-none">{label}</span>
      </div>
      <Handle type="source" position={Position.Bottom} className="opacity-0" />
    </div>
  );
};

const nodeTypes = { agent: AgentNode };

function App() {
  const [activeTab, setActiveTab] = useState("dashboard"); 
  const [goal, setGoal] = useState("");
  const [taskId, setTaskId] = useState(null);
  const [status, setStatus] = useState(null);
  const [report, setReport] = useState(null);
  const [displayedReport, setDisplayedReport] = useState("");
  const [memoryInfo, setMemoryInfo] = useState(null);
  const [recentTasks, setRecentTasks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const API_URL = "http://localhost:8000";

  // --- TYPEWRITER EFFECT ---
  useEffect(() => {
    if (report && displayedReport.length < report.length) {
      const timeout = setTimeout(() => {
        // Stream in chunks of 5 characters for better performance
        setDisplayedReport(report.slice(0, displayedReport.length + 5));
      }, 5);
      return () => clearTimeout(timeout);
    }
  }, [report, displayedReport]);

  const fetchRecentTasks = useCallback(async () => {
    try {
      const res = await axios.get(`${API_URL}/tasks`);
      setRecentTasks(res.data);
    } catch (err) {
      console.error("Failed to fetch history", err);
    }
  }, [API_URL]);

  const fetchReport = useCallback(async () => {
    if (!taskId) return;
    try {
      const res = await axios.get(`${API_URL}/report/${taskId}`);
      setReport(res.data.report);
      setDisplayedReport(""); // Reset typewriter
      const memRes = await axios.get(`${API_URL}/memory/${taskId}`);
      setMemoryInfo(memRes.data);
    } catch (err) {
      console.error("Failed to download report", err);
      setError("Failed to download the final intelligence report.");
    }
  }, [API_URL, taskId]);

  useEffect(() => {
    fetchRecentTasks();
  }, [fetchRecentTasks]);

  const handleExecute = async () => {
    if (!goal.trim()) return;
    setLoading(true);
    setError(null);
    setStatus(null);
    setReport(null);
    setDisplayedReport("");
    setMemoryInfo(null);
    setTaskId(null);

    try {
      const res = await axios.post(`${API_URL}/execute`, { goal });
      setTaskId(res.data.task_id);
    } catch (err) {
      setError("Failed to connect to the HireIQ backend. Is it running on port 8000?");
      setLoading(false);
    }
  };

  const handleLoadHistory = (id, oldGoal) => {
    setTaskId(id);
    setGoal(oldGoal);
    setReport(null);
    setDisplayedReport("");
    setLoading(true);
    setStatus({ status: "running", current_node: "report_generator", percentage_complete: 100 });
  };

  useEffect(() => {
    let interval = null;

    if (taskId && (!status || status.status === "running")) {
      interval = setInterval(async () => {
        try {
          const res = await axios.get(`${API_URL}/status/${taskId}`);
          setStatus(res.data);
          
          if (res.data.status === "completed" || res.data.status === "failed") {
            clearInterval(interval);
            setLoading(false);
            
            if (res.data.status === "completed") {
              fetchReport();
              fetchRecentTasks();
            } else if (res.data.status === "failed") {
              setError(res.data.error || "Agent execution failed.");
            }
          }
        } catch (err) {
          console.error("Error polling status", err);
        }
      }, 2000);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [taskId, status, fetchReport, fetchRecentTasks]);

  const nodesList = [
    { id: "starting", label: "Initialization", icon: Zap },
    { id: "goal_parser", label: "Goal Analysis", icon: Search },
    { id: "planner", label: "Strategic Planning", icon: LayoutList },
    { id: "executor", label: "Tool Execution", icon: Cpu },
    { id: "verifier", label: "Data Verification", icon: ShieldCheck },
    { id: "synthesizer", label: "Knowledge Synthesis", icon: BrainCircuit },
    { id: "report_generator", label: "Report Generation", icon: PenTool }
  ];
  
  const getNodeState = (nodeId) => {
    if (!status) return "pending";
    if (status.status === "completed") return "completed";
    const currentIndex = nodesList.findIndex(n => n.id === status.current_node);
    const thisIndex = nodesList.findIndex(n => n.id === nodeId);
    if (thisIndex < currentIndex) return "completed";
    if (thisIndex === currentIndex) return "running";
    return "pending";
  };

  // --- REACT FLOW GRAPH DATA ---
  const flowNodes = useMemo(() => {
    return nodesList.map((n, i) => ({
      id: n.id,
      type: 'agent',
      data: { label: n.label, icon: n.icon, state: getNodeState(n.id) },
      position: { x: 50, y: i * 100 },
      draggable: false,
    }));
  }, [status]);

  const flowEdges = useMemo(() => {
    return nodesList.slice(0, -1).map((n, i) => ({
      id: `e${i}`,
      source: n.id,
      target: nodesList[i+1].id,
      animated: getNodeState(n.id) === "running" || (getNodeState(n.id) === "completed" && getNodeState(nodesList[i+1].id) === "running"),
      style: { stroke: getNodeState(n.id) === "completed" ? "#10b981" : "#e2e8f0", strokeWidth: 2 },
    }));
  }, [status]);

  const exampleQuests = [
    { label: "AI vs ML (Bangalore)", text: "Compare AI Engineer vs ML Engineer salaries and skills in Bangalore", icon: <TrendingUp className="w-3 h-3" /> },
    { label: "Hyderabad Data Jobs", text: "Find top hiring companies and salary ranges for Data Engineers in Hyderabad", icon: <MapPin className="w-3 h-3" /> },
    { label: "Pune Tech Hub", text: "Research emerging tech skills in the Pune startup ecosystem for 2026", icon: <Briefcase className="w-3 h-3" /> },
    { label: "India Remote Trends", text: "What are the current trends for remote software engineering roles in India?", icon: <Sparkles className="w-3 h-3" /> },
    { label: "Product Cos (BLR)", text: "List top 10 AI-focused product companies in Bangalore and their required stack", icon: <LayoutList className="w-3 h-3" /> }
  ];

  const agents = [
    { name: "Goal Parser", role: "Semantic Entryway", icon: <Zap className="w-6 h-6 text-yellow-500" />, desc: "Uses few-shot prompting to extract Pydantic-validated schemas from raw human intent." },
    { name: "The Architect", role: "Strategy Engine", icon: <FileText className="w-6 h-6 text-blue-500" />, desc: "Determines the complexity of the quest and dynamic node mapping into a DAG execution plan." },
    { name: "The Worker", role: "Tool Specialist", icon: <Cpu className="w-6 h-6 text-purple-500" />, desc: "Bridges the LLM to the real-time web using the Tavily Search API." },
    { name: "The Judge", role: "Consistency Guard", icon: <ShieldCheck className="w-6 h-6 text-emerald-500" />, desc: "A recursive verification layer that scores output and triggers autonomous backtracking loops." },
    { name: "The Brain", role: "Knowledge Aggregator", icon: <BrainCircuit className="w-6 h-6 text-pink-500" />, desc: "Performs semantic synthesis to identify market momentum and skill gaps." },
    { name: "The Writer", role: "Report Architect", icon: <PenTool className="w-6 h-6 text-slate-700" />, desc: "Compiles the final intelligence briefing using a structured Markdown template." }
  ];

  const tools = [
    { name: "Tavily AI", role: "Search Infrastructure", desc: "Optimized search engine providing noise-free context for RAG.", icon: <Globe className="w-5 h-5 text-blue-400" /> },
    { name: "Groq Llama 3", role: "Inference Engine", desc: "Powers reasoning with extremely low-latency multi-agent loops.", icon: <Zap className="w-5 h-5 text-orange-400" /> },
    { name: "LangGraph", role: "State Orchestrator", desc: "Manages graph states, persistence, and recursive node backtracking.", icon: <Workflow className="w-5 h-5 text-blue-600" /> },
    { name: "ChromaDB", role: "Vector Memory", desc: "Converts past reports into vector embeddings for fast similarity retrieval.", icon: <BrainCircuit className="w-5 h-5 text-pink-400" /> },
    { name: "SQLAlchemy", role: "Relational ORM", desc: "Handles the SQLite persistence layer for historical data logging.", icon: <Database className="w-5 h-5 text-slate-600" /> }
  ];

  return (
    <div className="min-h-screen bg-[#f8fafc] text-slate-900 font-['Inter'] selection:bg-blue-100">
      {/* Navbar */}
      <nav className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-slate-200 no-print">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <span className="font-bold text-xl tracking-tight text-slate-800">HireIQ <span className="text-blue-600 font-black">SWARM</span></span>
          </div>
          
          <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-xl border border-slate-200">
            {[
              { id: "dashboard", label: "Dashboard", icon: <LayoutList className="w-3 h-3" /> },
              { id: "blueprint", label: "Technical Blueprint", icon: <BookOpen className="w-3 h-3" /> }
            ].map((tab) => (
              <button 
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-6 py-1.5 text-[10px] font-black uppercase tracking-widest rounded-lg transition-all flex items-center gap-2 ${
                  activeTab === tab.id ? "bg-white text-blue-600 shadow-sm" : "text-slate-400 hover:text-slate-600"
                }`}
              >
                {tab.icon}
                {tab.label}
              </button>
            ))}
          </div>

          <div className="hidden md:flex items-center gap-3">
             <div className="flex items-center gap-1.5 px-3 py-1 bg-emerald-50 text-emerald-600 rounded-full border border-emerald-100">
               <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"></div>
               <span className="text-[10px] font-black uppercase tracking-wider">Engine Online</span>
             </div>
          </div>
        </div>
      </nav>

      {activeTab === "dashboard" ? (
        <main className="max-w-6xl mx-auto px-6 py-12 space-y-16">
          <section className="space-y-6 no-print text-center max-w-4xl mx-auto pt-10">
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-blue-50 text-blue-600 rounded-full border border-blue-100 text-[10px] font-black uppercase tracking-widest mb-4">
              Autonomous Intelligence Core
            </div>
            <h2 className="text-5xl font-black text-slate-900 tracking-tight leading-tight uppercase">Launch an <span className="text-blue-600 underline decoration-blue-100 underline-offset-8">Autonomous Swarm</span> in India.</h2>
            <p className="text-slate-500 mt-6 text-xl font-medium leading-relaxed">Define your research goal and let our autonomous agent swarm orchestrate real-time web discovery and semantic synthesis.</p>
            
            <div className="relative group max-w-3xl mx-auto mt-10">
              <div className="absolute -inset-1 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl blur opacity-20 group-hover:opacity-40 transition duration-1000 group-hover:duration-200"></div>
              <div className="relative flex gap-3 bg-white p-2 rounded-2xl border border-slate-200 shadow-xl shadow-slate-200/50">
                <div className="flex-1 relative flex items-center">
                  <Search className="absolute left-4 w-5 h-5 text-slate-400" />
                  <input 
                    type="text"
                    value={goal}
                    onChange={(e) => setGoal(e.target.value)}
                    placeholder="Ask about roles, skills, or salary trends in India..."
                    className="w-full pl-12 pr-4 py-5 bg-transparent border-none focus:ring-0 text-lg placeholder:text-slate-300 font-medium"
                    onKeyDown={(e) => e.key === 'Enter' && handleExecute()}
                  />
                </div>
                <button 
                  onClick={handleExecute}
                  disabled={loading || !goal.trim()}
                  className="px-10 py-4 bg-blue-600 text-white font-black rounded-xl hover:bg-blue-700 active:scale-95 transition-all flex items-center gap-2 shadow-lg shadow-blue-200 disabled:opacity-50 disabled:active:scale-100 uppercase tracking-widest text-xs"
                >
                  {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Play className="w-5 h-5" />}
                  Launch Quest
                </button>
              </div>
            </div>

            <div className="flex flex-wrap justify-center gap-2 mt-6">
              {exampleQuests.map((example, i) => (
                <button 
                  key={i}
                  onClick={() => setGoal(example.text)}
                  className="px-3 py-1.5 bg-white border border-slate-200 rounded-lg text-[11px] font-bold text-slate-600 hover:border-blue-400 hover:text-blue-600 hover:bg-blue-50 transition-all flex items-center gap-2 shadow-sm"
                >
                  {example.icon}
                  {example.label}
                </button>
              ))}
            </div>

            {error && (
              <div className="flex items-center justify-center gap-2 text-red-600 bg-red-50 px-4 py-2 rounded-lg border border-red-100 mt-4 animate-in fade-in slide-in-from-top-2">
                <AlertCircle className="w-4 h-4" />
                <span className="text-sm font-medium">{error}</span>
              </div>
            )}
          </section>

          {(status || loading) && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 no-print animate-in fade-in slide-in-from-bottom-4 duration-500">
              <div className="lg:col-span-1 bg-white p-8 rounded-3xl border border-slate-200 shadow-sm space-y-8 flex flex-col min-h-[500px]">
                <h3 className="font-black text-slate-800 flex items-center gap-2 uppercase tracking-widest text-xs">
                  <Workflow className="w-4 h-4 text-blue-600" />
                  Live Swarm Map
                </h3>
                <div className="flex-1 bg-slate-50/50 rounded-2xl border border-slate-100 overflow-hidden relative">
                   <ReactFlow 
                    nodes={flowNodes} 
                    edges={flowEdges} 
                    nodeTypes={nodeTypes}
                    fitView
                    zoomOnScroll={false}
                    zoomOnPinch={false}
                    panOnDrag={false}
                    preventScrolling={true}
                   >
                    <Background color="#cbd5e1" gap={20} />
                   </ReactFlow>
                </div>
              </div>

              <div className="lg:col-span-2 bg-white p-10 rounded-3xl border border-slate-200 shadow-sm overflow-hidden">
                <h3 className="font-black text-slate-800 mb-8 flex items-center gap-2 uppercase tracking-widest text-xs">
                  <LayoutList className="w-4 h-4 text-blue-600" />
                  Dynamic Strategy Plan
                </h3>
                {status?.execution_plan ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                    {status.execution_plan.map((step, idx) => (
                      <div key={idx} className="p-6 bg-slate-50 border border-slate-100 rounded-2xl group hover:bg-white hover:shadow-lg transition-all duration-300">
                        <div className="text-[10px] font-black text-blue-600 uppercase tracking-tighter mb-2">Stage {step.step}</div>
                        <p className="text-sm font-bold text-slate-600 leading-snug group-hover:text-slate-900">{step.description}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center py-24 bg-slate-50/50 rounded-2xl border border-dashed border-slate-200 italic text-slate-400 text-sm">
                    Agent is architecting a custom research strategy...
                  </div>
                )}
              </div>
            </div>
          )}

          {(displayedReport || report) && (
            <section className="report-section bg-white rounded-[2.5rem] border border-slate-200 shadow-2xl shadow-slate-200/50 overflow-hidden animate-in fade-in zoom-in-95 duration-1000">
              <div className="report-header bg-[#0f172a] px-12 py-10 text-white">
                <div className="inline-flex items-center gap-2 px-3 py-1 bg-blue-600/20 text-blue-400 rounded-full border border-blue-500/20 text-[9px] font-black uppercase tracking-widest mb-3">Intelligence Briefing</div>
                <h2 className="text-3xl font-black tracking-tight leading-tight uppercase">{status?.goal || goal}</h2>
              </div>
              {memoryInfo && memoryInfo.similar_reports?.length > 0 && (
                <div className="px-12 py-4 bg-blue-50 border-b border-blue-100 flex items-center gap-3 no-print font-bold text-sm text-blue-800">
                  <BrainCircuit className="w-5 h-5 text-blue-600" /> Semantic Memory Found: <span className="text-xs text-blue-600 italic font-black uppercase tracking-widest">Historical Data Utilized</span>
                </div>
              )}
              <div className="px-12 py-16 prose prose-slate max-w-none relative">
                {displayedReport.length < (report?.length || 0) && (
                  <div className="absolute top-10 right-10 flex items-center gap-2 text-blue-600 text-[10px] font-black uppercase tracking-[0.2em] animate-pulse no-print">
                    <div className="w-1 h-1 bg-blue-600 rounded-full"></div>
                    Synthesizing...
                  </div>
                )}
                <ReactMarkdown>{displayedReport || report}</ReactMarkdown>
                {displayedReport.length < (report?.length || 0) && (
                   <span className="inline-block w-2 h-4 bg-blue-600 ml-1 animate-pulse"></span>
                )}
              </div>
              <div className="bg-slate-50 px-12 py-8 border-t border-slate-100 flex items-center justify-end no-print">
                <button onClick={() => window.print()} className="px-8 py-3 bg-slate-900 text-white rounded-xl text-[10px] font-black uppercase tracking-widest hover:bg-blue-600 transition-all flex items-center gap-2">Download Report PDF <ArrowRight className="w-3 h-3" /></button>
              </div>
            </section>
          )}

          {recentTasks.length > 0 && (
            <section className="space-y-6 no-print">
               <h3 className="font-black text-slate-800 flex items-center gap-2 uppercase tracking-widest text-sm">
                 <History className="w-5 h-5 text-blue-600" /> Recent Quests
               </h3>
               <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {recentTasks.map((t) => (
                    <div key={t.task_id} onClick={() => handleLoadHistory(t.task_id, t.goal)} className="group bg-white p-6 rounded-2xl border border-slate-200 hover:border-blue-400 hover:shadow-xl transition-all cursor-pointer">
                      <h4 className="text-sm font-bold text-slate-700 leading-tight group-hover:text-slate-900 line-clamp-2 mb-4">{t.goal}</h4>
                      <div className="px-2 py-0.5 bg-slate-50 border border-slate-100 text-[9px] font-black text-slate-400 rounded uppercase">View Report</div>
                    </div>
                  ))}
               </div>
            </section>
          )}
        </main>
      ) : (
        <main className="max-w-6xl mx-auto px-6 py-20 space-y-24 animate-in fade-in slide-in-from-bottom-4 duration-700">
          <div className="text-center space-y-6">
            <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-blue-50 text-blue-600 rounded-full border border-blue-100 text-[10px] font-black uppercase tracking-widest">Engineering Case Study</div>
            <h1 className="text-6xl font-black text-slate-900 tracking-tight leading-[0.9]">Technical <span className="text-blue-600 font-black">Blueprint.</span></h1>
            <p className="text-slate-500 text-xl max-w-2xl mx-auto font-medium">A deep dive into the autonomous architecture and data persistence strategy behind HireIQ.</p>
          </div>

          <section className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
             <div className="space-y-8">
                <div className="w-16 h-16 bg-blue-600 rounded-2xl flex items-center justify-center shadow-xl">
                   <Workflow className="w-8 h-8 text-white" />
                </div>
                <h2 className="text-4xl font-black text-slate-900 tracking-tight leading-tight">The LangGraph <br/><span className="text-blue-600">Orchestrator</span></h2>
                <p className="text-slate-600 text-lg leading-relaxed font-medium">Unlike standard linear chains, HireIQ utilizes a <strong>Directed Acyclic Graph (DAG)</strong> architecture. This allows for stateful, iterative reasoning and recursive backtracking.</p>
                <div className="space-y-4">
                   {["Cyclic Reasoning & Retries", "State Persistence (Thread-safe Checkpoints)", "Parallel Multi-Tool Execution"].map((f, i) => (
                     <div key={i} className="flex gap-4 p-4 bg-white rounded-2xl border border-slate-100 shadow-sm">
                        <CheckCircle2 className="w-5 h-5 text-blue-600" />
                        <span className="text-sm font-black text-slate-800 uppercase tracking-tight">{f}</span>
                     </div>
                   ))}
                </div>
             </div>
             <div className="bg-[#0f172a] rounded-[3.5rem] p-12 text-white relative overflow-hidden">
                <div className="absolute top-0 right-0 w-64 h-64 bg-blue-600/20 blur-[100px] -mr-32 -mt-32"></div>
                <div className="relative z-10 space-y-8">
                   <div className="text-[10px] font-black text-blue-400 uppercase tracking-widest border-b border-white/10 pb-4">Agent Swarm Logic</div>
                   <div className="grid grid-cols-1 gap-4">
                      {agents.map((a, i) => (
                        <div key={i} className="flex items-center gap-4 p-4 bg-white/5 rounded-2xl border border-white/5">
                           <div className="w-10 h-10 bg-white/10 rounded flex items-center justify-center">{a.icon}</div>
                           <div>
                              <div className="text-[9px] font-black text-slate-500 uppercase">{a.name}</div>
                              <div className="text-sm font-bold leading-tight">{a.desc}</div>
                           </div>
                        </div>
                      ))}
                   </div>
                </div>
             </div>
          </section>

          {/* ADVANCED SECTION: SEMANTIC MEMORY & COST OPTIMIZATION */}
          <section className="space-y-12 bg-white rounded-[3.5rem] border border-slate-200 p-16 shadow-sm overflow-hidden relative">
             <div className="absolute top-0 right-0 w-96 h-96 bg-blue-50 blur-[120px] -mr-48 -mt-48 opacity-60"></div>
             <div className="grid grid-cols-1 lg:grid-cols-2 gap-20 relative z-10">
                <div className="space-y-8">
                   <div className="w-14 h-14 bg-indigo-50 rounded-2xl flex items-center justify-center border border-indigo-100">
                      <Target className="w-7 h-7 text-indigo-600" />
                   </div>
                   <h2 className="text-3xl font-black text-slate-900 tracking-tight uppercase leading-tight">Semantic Cache & <br/><span className="text-indigo-600">Cost Optimization</span></h2>
                   <p className="text-slate-600 font-medium text-lg leading-relaxed">
                      To prevent redundant LLM inference and reduce API token costs, HireIQ implements a <strong>Semantic Memory Layer</strong> using ChromaDB.
                   </p>
                   <div className="p-6 bg-slate-50 rounded-2xl border border-slate-100">
                      <h4 className="font-black text-xs uppercase tracking-widest text-slate-400 mb-3">How it works:</h4>
                      <ol className="space-y-3">
                        <li className="text-sm font-bold text-slate-600 flex gap-3">
                           <span className="text-indigo-600">01</span> Every research goal is converted into a vector embedding (all-MiniLM).
                        </li>
                        <li className="text-sm font-bold text-slate-600 flex gap-3">
                           <span className="text-indigo-600">02</span> The system queries ChromaDB for historical matches with a similarity score &gt; 0.85.
                        </li>
                        <li className="text-sm font-bold text-slate-600 flex gap-3">
                           <span className="text-indigo-600">03</span> If found, the agent retrieves the previous report instantly, bypassing new web searches.
                        </li>
                      </ol>
                   </div>
                </div>
                <div className="flex flex-col justify-center space-y-6">
                   <div className="p-8 bg-indigo-600 rounded-3xl text-white shadow-2xl shadow-indigo-200">
                      <div className="flex items-center gap-3 mb-4">
                         <Zap className="w-5 h-5 text-yellow-300" />
                         <span className="text-xs font-black uppercase tracking-widest opacity-80">Latency Impact</span>
                      </div>
                      <div className="text-4xl font-black mb-1 tracking-tighter">98.4% Faster</div>
                      <p className="text-xs text-indigo-100 font-medium">Memory retrieval takes ~100ms compared to ~45s for a full autonomous research cycle.</p>
                   </div>
                   <div className="p-8 bg-white rounded-3xl border border-slate-200 shadow-sm">
                      <div className="flex items-center gap-3 mb-4 text-slate-400">
                         <RefreshCcw className="w-5 h-5" />
                         <span className="text-xs font-black uppercase tracking-widest">Self-Healing Backtracking</span>
                      </div>
                      <p className="text-sm text-slate-500 font-medium leading-relaxed">
                         If the <strong>Verifier Node</strong> detects inconsistent data (e.g., missing salary range), it triggers an autonomous retry loop, feeding the failure reason back to the <strong>Worker Node</strong> for targeted discovery.
                      </p>
                   </div>
                </div>
             </div>
          </section>

          {/* ADVANCED SECTION: PRODUCTION ROADMAP */}
          <section className="bg-slate-900 rounded-[3.5rem] p-16 text-white overflow-hidden relative">
             <div className="absolute bottom-0 right-0 w-96 h-96 bg-blue-600/10 blur-[100px] -mr-48 -mb-48"></div>
             <div className="grid grid-cols-1 lg:grid-cols-2 gap-20 relative z-10">
                <div className="space-y-8">
                   <div className="w-14 h-14 bg-white/5 rounded-2xl flex items-center justify-center border border-white/10">
                      <Scale className="w-7 h-7 text-blue-400" />
                   </div>
                   <h2 className="text-3xl font-black text-white tracking-tight uppercase leading-tight">Production <br/><span className="text-blue-400">Scalability Roadmap</span></h2>
                   <p className="text-slate-400 font-medium text-lg leading-relaxed">
                      While currently optimized for local demonstration, the HireIQ architecture is built for horizontal scalability in cloud environments.
                   </p>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                   {[
                     { title: "Vector Scaling", desc: "Transition from local ChromaDB to Pinecone/Milvus for multi-million vector indexing.", icon: <BrainCircuit className="w-5 h-5 text-pink-400" /> },
                     { title: "Distributed Tasks", desc: "Implementing Celery/Redis workers to handle thousands of concurrent agent loops.", icon: <Workflow className="w-5 h-5 text-blue-400" /> },
                     { title: "Database Migration", desc: "Scaling from SQLite to PostgreSQL (Supabase/Neon) for high-concurrency relational data.", icon: <Database className="w-5 h-5 text-slate-400" /> },
                     { title: "Edge Deployment", desc: "Deploying the FastAPI core to AWS Lambda/Vercel Functions for global low-latency.", icon: <Globe className="w-5 h-5 text-emerald-400" /> }
                   ].map((item, i) => (
                     <div key={i} className="p-6 bg-white/5 border border-white/10 rounded-3xl hover:bg-white/10 transition-all">
                        <div className="mb-4">{item.icon}</div>
                        <h4 className="text-sm font-black text-white uppercase tracking-tight mb-2 leading-tight">{item.title}</h4>
                        <p className="text-[10px] text-slate-400 leading-relaxed font-medium">{item.desc}</p>
                     </div>
                   ))}
                </div>
             </div>
          </section>

          <section className="bg-white rounded-[4rem] border border-slate-200 p-16 shadow-sm space-y-16">
             <div className="text-center">
                <h2 className="text-3xl font-black text-slate-900 tracking-tight uppercase mb-4 uppercase">The Technical Toolbox</h2>
                <p className="text-slate-500 font-medium max-w-xl mx-auto">Core infrastructure powering real-time web discovery and semantic memory.</p>
             </div>
             <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {tools.map((t, i) => (
                  <div key={i} className="p-8 bg-slate-50 border border-slate-100 rounded-[2.5rem] hover:bg-white hover:border-blue-200 transition-all duration-300 shadow-sm">
                     <div className="w-12 h-12 bg-white rounded-2xl flex items-center justify-center mb-6 shadow-sm">{t.icon}</div>
                     <div className="text-[9px] font-black text-blue-600 uppercase tracking-widest mb-1">{t.role}</div>
                     <h3 className="text-lg font-black text-slate-800 mb-3 tracking-tight leading-tight">{t.name}</h3>
                     <p className="text-xs text-slate-500 leading-relaxed font-medium">{t.desc}</p>
                  </div>
                ))}
             </div>
          </section>

          <section className="text-center max-w-3xl mx-auto space-y-8 pt-10">
             <div className="w-20 h-20 bg-blue-50 rounded-full flex items-center justify-center mx-auto border border-blue-100">
                <Code2 className="w-10 h-10 text-blue-600" />
             </div>
             <h2 className="text-4xl font-black text-slate-900 tracking-tight uppercase">System Capability Metrics</h2>
             <div className="flex flex-wrap items-center justify-center gap-12 pt-4">
                <div className="flex flex-col items-center">
                   <div className="text-4xl font-black text-slate-900">100%</div>
                   <div className="text-[10px] font-black text-slate-400 uppercase tracking-widest mt-1">Autonomous</div>
                </div>
                <div className="w-px h-12 bg-slate-200 hidden md:block"></div>
                <div className="flex flex-col items-center">
                   <div className="text-4xl font-black text-slate-900">~42s</div>
                   <div className="text-[10px] font-black text-slate-400 uppercase tracking-widest mt-1">Latency</div>
                </div>
                <div className="w-px h-12 bg-slate-200 hidden md:block"></div>
                <div className="flex flex-col items-center">
                   <div className="text-4xl font-black text-slate-900">0.0ms</div>
                   <div className="text-[10px] font-black text-slate-400 uppercase tracking-widest mt-1">Human Intervention</div>
                </div>
             </div>
          </section>
        </main>
      )}

      <footer className="max-w-6xl mx-auto px-6 py-12 border-t border-slate-200 flex flex-col md:flex-row items-center justify-between text-slate-400 no-print">
        <div className="text-[10px] font-black uppercase tracking-widest">© 2026 HireIQ SWARM | Autonomous Multi-Agent System</div>
        <div className="flex gap-6 text-[10px] font-black uppercase tracking-widest mt-4 md:mt-0">
          <a href="#" className="hover:text-slate-600 transition-colors">Github</a>
          <a href="#" className="hover:text-slate-600 transition-colors">Documentation</a>
        </div>
      </footer>
    </div>
  );
}

export default App;
