import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Loader2, Download, Code2, Box, History, Trash2, RotateCcw } from 'lucide-react'
import { Viewer } from './Viewer'

const API_URL = 'http://localhost:8001'

const examples = [
  'A box 50x30x20mm with 3mm fillets',
  'Cylinder with a hole through the center',
  'L-bracket with mounting holes',
  'Hex nut M10',
  'Simple gear 20 teeth',
]

interface ModelInfo {
  width_mm: number
  depth_mm: number
  height_mm: number
  volume_cm3: number
  surface_area_cm2: number
}

interface GenerateResult {
  code: string
  stl_url: string
  step_url: string
  dxf_url: string
  error?: string
  model_info?: ModelInfo
  session_id?: string
  edits_remaining?: number
}

interface HistoryItem {
  id: number
  prompt: string
  result: GenerateResult
  timestamp: Date
}

export default function App() {
  const [prompt, setPrompt] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<GenerateResult | null>(null)
  const [error, setError] = useState('')
  const [showCode, setShowCode] = useState(false)
  const [history, setHistory] = useState<HistoryItem[]>([])
  const [showHistory, setShowHistory] = useState(false)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [editsRemaining, setEditsRemaining] = useState<number | null>(null)

  const handleGenerate = async (text?: string) => {
    const q = (text ?? prompt).trim()
    if (!q || loading) return
    setPrompt(q)
    setLoading(true)
    setError('')
    setResult(null)

    try {
      const res = await fetch(`${API_URL}/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: q, session_id: sessionId }),
      })
      const data = await res.json()
      if (!res.ok) {
        setError(data.detail || 'Generation failed')
      } else if (data.error) {
        setError(data.error)
        setResult(data)
      } else {
        setResult(data)
        if (data.session_id) setSessionId(data.session_id)
        if (data.edits_remaining !== undefined) setEditsRemaining(data.edits_remaining)
        setHistory((prev) => [
          { id: Date.now(), prompt: q, result: data, timestamp: new Date() },
          ...prev,
        ])
      }
    } catch {
      setError('Cannot reach backend. Is it running on port 8001?')
    }

    setLoading(false)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleGenerate()
    }
  }

  return (
    <div className="h-full flex flex-col bg-neutral-50">
      {/* Header */}
      <header className="h-12 border-b border-neutral-200 bg-white flex items-center px-4 shrink-0">
        <Box size={18} className="text-indigo-500" />
        <span className="ml-2 text-sm font-semibold text-neutral-800">CadGen</span>
        <span className="ml-2 text-xs text-neutral-400">Text to CAD</span>
        <div className="ml-auto flex items-center gap-2">
          <button
            onClick={() => setShowHistory(!showHistory)}
            className={`flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-medium rounded-lg transition-colors ${
              showHistory ? 'bg-indigo-50 text-indigo-600' : 'text-neutral-500 hover:text-indigo-600 hover:bg-indigo-50'
            }`}
          >
            <History size={14} />
            History ({history.length})
          </button>
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden">
        {/* Left panel — prompt + code */}
        <div className="w-100 border-r border-neutral-200 bg-white flex flex-col shrink-0">
          {/* Input */}
          <div className="p-4 border-b border-neutral-100">
            <div className="relative">
              <textarea
                value={prompt}
                onChange={(e) => {
                  setPrompt(e.target.value)
                  e.target.style.height = 'auto'
                  e.target.style.height = Math.min(e.target.scrollHeight, 200) + 'px'
                }}
                onKeyDown={handleKeyDown}
                placeholder="Describe a 3D part..."
                disabled={loading}
                rows={1}
                className="w-full rounded-xl border border-neutral-300 bg-white px-4 py-3 pr-12 text-sm text-neutral-800 placeholder:text-neutral-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 disabled:opacity-50 resize-none overflow-y-auto"
                style={{ maxHeight: '200px' }}
              />
              <button
                onClick={() => handleGenerate()}
                disabled={loading || !prompt.trim() || editsRemaining === 0}
                className="absolute right-2 top-1/2 -translate-y-1/2 w-8 h-8 rounded-lg bg-indigo-500 text-white flex items-center justify-center disabled:bg-neutral-200 disabled:text-neutral-400 hover:bg-indigo-600 transition-colors"
              >
                {loading ? <Loader2 size={14} className="animate-spin" /> : <Send size={14} />}
              </button>
            </div>
          </div>

          {/* Examples */}
          {!result && !loading && (
            <div className="p-4 border-b border-neutral-100">
              <p className="text-xs text-neutral-400 mb-2">Try an example:</p>
              <div className="flex flex-wrap gap-1.5">
                {examples.map((ex) => (
                  <button
                    key={ex}
                    onClick={() => handleGenerate(ex)}
                    className="text-xs px-2.5 py-1.5 border border-neutral-200 rounded-lg text-neutral-600 hover:border-indigo-300 hover:text-indigo-600 transition-colors"
                  >
                    {ex}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Loading */}
          {loading && (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <Loader2 size={24} className="animate-spin text-indigo-500 mx-auto mb-2" />
                <p className="text-sm text-neutral-500">Generating CAD model...</p>
              </div>
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="p-4">
              <div className="bg-red-50 border border-red-200 rounded-xl p-3 text-sm text-red-600">
                {error}
              </div>
            </div>
          )}

          {/* Result controls */}
          {result && !error && (
            <div className="p-4 space-y-3">
              <div className="flex gap-2">
                <a
                  href={`${API_URL}${result.step_url}`}
                  className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 bg-indigo-500 text-white text-sm font-medium rounded-xl hover:bg-indigo-600 transition-colors"
                >
                  <Download size={14} />
                  STEP
                </a>
                <a
                  href={`${API_URL}${result.stl_url}`}
                  className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 bg-neutral-800 text-white text-sm font-medium rounded-xl hover:bg-neutral-900 transition-colors"
                >
                  <Download size={14} />
                  STL
                </a>
                {result.dxf_url && (
                  <a
                    href={`${API_URL}${result.dxf_url}`}
                    className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 bg-teal-600 text-white text-sm font-medium rounded-xl hover:bg-teal-700 transition-colors"
                  >
                    <Download size={14} />
                    DXF
                  </a>
                )}
              </div>
              {result.model_info && (
                <div className="bg-neutral-50 border border-neutral-200 rounded-xl p-3 space-y-1.5">
                  <p className="text-[10px] font-semibold text-neutral-500 uppercase tracking-wide">Model Info</p>
                  <div className="grid grid-cols-2 gap-x-4 gap-y-1">
                    <div className="text-xs text-neutral-600">
                      <span className="text-neutral-400">W:</span> {result.model_info.width_mm}mm
                    </div>
                    <div className="text-xs text-neutral-600">
                      <span className="text-neutral-400">D:</span> {result.model_info.depth_mm}mm
                    </div>
                    <div className="text-xs text-neutral-600">
                      <span className="text-neutral-400">H:</span> {result.model_info.height_mm}mm
                    </div>
                    <div className="text-xs text-neutral-600">
                      <span className="text-neutral-400">Vol:</span> {result.model_info.volume_cm3} cm³
                    </div>
                    <div className="text-xs text-neutral-600 col-span-2">
                      <span className="text-neutral-400">Surface:</span> {result.model_info.surface_area_cm2} cm²
                    </div>
                  </div>
                </div>
              )}

              {/* Edit counter & New Design button */}
              <div className="flex items-center justify-between">
                {editsRemaining !== null && editsRemaining > 0 && (
                  <span className="text-xs text-neutral-500">
                    {editsRemaining} edit{editsRemaining !== 1 ? 's' : ''} remaining
                  </span>
                )}
                {editsRemaining === 0 && (
                  <span className="text-xs text-amber-600 font-medium">No edits remaining</span>
                )}
                <button
                  onClick={() => {
                    setSessionId(null)
                    setEditsRemaining(null)
                    setResult(null)
                    setPrompt('')
                    setError('')
                    setShowCode(false)
                  }}
                  className="flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-lg bg-indigo-50 text-indigo-600 hover:bg-indigo-100 transition-colors"
                >
                  <RotateCcw size={12} />
                  New Design
                </button>
              </div>

              <button
                onClick={() => setShowCode(!showCode)}
                className={`flex items-center gap-1.5 text-xs font-medium px-2.5 py-1.5 rounded-lg transition-colors ${
                  showCode ? 'bg-blue-50 text-blue-600' : 'text-neutral-400 hover:text-blue-600 hover:bg-blue-50'
                }`}
              >
                <Code2 size={12} />
                {showCode ? 'Hide code' : 'View code'}
              </button>
              <AnimatePresence>
                {showCode && (
                  <motion.pre
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="overflow-y-auto max-h-60 bg-neutral-50 border border-neutral-200 rounded-xl p-3 text-xs font-mono text-neutral-600 whitespace-pre-wrap"
                  >
                    {result.code}
                  </motion.pre>
                )}
              </AnimatePresence>
            </div>
          )}
        </div>

        {/* History panel */}
        <AnimatePresence>
          {showHistory && (
            <motion.div
              initial={{ width: 0, opacity: 0 }}
              animate={{ width: 280, opacity: 1 }}
              exit={{ width: 0, opacity: 0 }}
              className="border-r border-neutral-200 bg-white flex flex-col overflow-hidden shrink-0"
            >
              <div className="p-3 border-b border-neutral-100 flex items-center justify-between">
                <span className="text-xs font-semibold text-neutral-700">Generation History</span>
                {history.length > 0 && (
                  <button
                    onClick={() => setHistory([])}
                    className="text-xs text-neutral-400 hover:text-red-500 transition-colors"
                  >
                    <Trash2 size={12} />
                  </button>
                )}
              </div>
              <div className="flex-1 overflow-y-auto">
                {history.length === 0 ? (
                  <div className="p-4 text-xs text-neutral-400 text-center">
                    No history yet. Generate a model to see it here.
                  </div>
                ) : (
                  history.map((item) => (
                    <button
                      key={item.id}
                      onClick={() => {
                        setResult(item.result)
                        setPrompt(item.prompt)
                        setError('')
                      }}
                      className="w-full text-left p-3 border-b border-neutral-50 hover:bg-indigo-50 transition-colors group"
                    >
                      <p className="text-xs text-neutral-700 font-medium line-clamp-2 group-hover:text-indigo-700">
                        {item.prompt}
                      </p>
                      <p className="text-[10px] text-neutral-400 mt-1">
                        {item.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </p>
                    </button>
                  ))
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Right panel — 3D viewer */}
        <div className="flex-1 bg-neutral-100 relative">
          {result && !error ? (
            <Viewer stlUrl={`${API_URL}${result.stl_url}`} />
          ) : loading ? (
            <div className="h-full flex items-center justify-center">
              <div className="flex flex-col items-center gap-4">
                <div className="relative w-20 h-20">
                  <motion.div
                    className="absolute inset-0 border-2 border-neutral-300 rounded-lg"
                    animate={{ rotateY: 360, rotateX: 360 }}
                    transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
                    style={{ transformStyle: 'preserve-3d' }}
                  />
                  <motion.div
                    className="absolute inset-2 border-2 border-neutral-400 rounded-md"
                    animate={{ rotateY: -360, rotateZ: 360 }}
                    transition={{ duration: 2.5, repeat: Infinity, ease: 'linear' }}
                    style={{ transformStyle: 'preserve-3d' }}
                  />
                  <motion.div
                    className="absolute inset-4 border-2 border-neutral-500 rounded-sm"
                    animate={{ rotateX: 360, rotateZ: -360 }}
                    transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                    style={{ transformStyle: 'preserve-3d' }}
                  />
                </div>
                <motion.p
                  className="text-sm text-neutral-500"
                  animate={{ opacity: [0.5, 1, 0.5] }}
                  transition={{ duration: 2, repeat: Infinity }}
                >
                  Building your model...
                </motion.p>
              </div>
            </div>
          ) : (
            <div className="h-full flex items-center justify-center text-neutral-400 text-sm">
              3D preview will appear here
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
