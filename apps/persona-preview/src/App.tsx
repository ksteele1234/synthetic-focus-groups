
import React, { useMemo, useState } from "react";

// Minimal, dependency-free preview to ensure canvas renders.
// Tailwind utility classes are available in the preview.

// --- Mock data (replace with API calls to your FastAPI backend) ---
const MOCK_QUOTES = [
  {
    source_type: "reddit",
    community: "r/Dynamics365",
    published_at: "2025-08-19",
    upvotes: 128,
    span:
      "We lost a week reconciling timesheets after migrating to Project Ops. The milestone template kept duplicating entries and our auditors hated it.",
    url: "https://www.reddit.com/r/Dynamics365/comments/abc123",
    stance: "pain",
    topics: ["timesheets", "migration"],
  },
  {
    source_type: "quora",
    community: "Microsoft Dynamics Project Operations",
    published_at: "2025-07-03",
    upvotes: 54,
    span:
      "If you set up billing milestones without aligning resource calendars, your revenue recognition will drift by a full cycle. Learned that the hard way.",
    url: "https://www.quora.com/q/xyz987",
    stance: "howto",
    topics: ["billing", "milestones"],
  },
  {
    source_type: "reddit",
    community: "r/GoHighLevel",
    published_at: "2025-08-30",
    upvotes: 77,
    span:
      "Switching to GHL saved us money but the handoff between chat and phone is messy. I want one timeline for every lead, not three.",
    url: "https://www.reddit.com/r/GoHighLevel/comments/def456",
    stance: "desire",
    topics: ["handoff", "crm"],
  },
];

const MOCK_PERSONAS = [
  {
    label: "Nashville Nick",
    demographics: {
      age: "34–42",
      gender: "Male",
      location: "Nashville, TN",
      education: "B.S. Accounting; CPA",
      income: "$140k–$220k",
    },
    psychographics: {
      values: ["reliability", "client trust", "work-life balance"],
      interests: ["SEC football", "live music", "smoked BBQ"],
      personality: "Pragmatic, risk-aware, direct",
      lifestyle: {
        home_life: "Married, two children under 8; coaches little league",
        work_life: "Firm partner-track, juggles billables and BD",
        family: "Parents nearby, strong church community",
        hobbies: ["golf", "smoking brisket", "weekend hikes"],
        community: "Chamber of Commerce, Rotary Club",
      },
    },
    jobs_to_be_done: [
      "Win higher-margin clients without adding staff",
      "Standardize proposals, onboarding, and monthly reviews",
    ],
    goals: ["Decrease admin time 30%", "Grow MRR by $25k in 2 quarters"],
    triggers: ["Tax season burnout", "Lost a prospect due to slow follow-up"],
    risk_tolerance: "Moderate",
    sophistication: "Tools-comfortable, not a tinkerer",
    narrative:
      "Nick runs a growing Nashville CPA practice. His mornings start with client emails and nudging staff on timesheets. He values predictable systems more than flashy tools. At home he’s present but protective of weekends. He’ll invest if the ROI is concrete and the rollout won’t hijack tax season. Hypothesis: He’s frustrated with juggling 3–4 apps that don’t sync timelines.",
  },
];

const PROMPT_TEMPLATE = `SYSTEM:
You are a buyer persona research strategist. Generate a complete, emotionally rich, narrative-driven persona document that matches the depth, style, and structure of the 'Nashville Nick' example. Your output must:
- Include narrative paragraphs plus direct quotes in the persona's own voice.
- Meet minimum word counts per section.
- Map fears, hopes, and outcomes to specific relationships (spouse, kids, peers, employees, clients).
- Produce both practical and emotional dimensions.
- End with a day-in-the-life scenario after the ideal solution.
- Strictly conform to the JSON schema provided.

USER:
Create a detailed buyer persona document with sections 1–11 as specified.

REQUIREMENTS:
- Each section: 150–200+ words.
- ≥2 direct quotes per section where applicable.
- Separate practical vs emotional outcomes.
- Day-in-life: ≥10 hourly blocks.

OUTPUT: Strictly follow the JSON schema.`;

const JSON_SCHEMA = `{
  "buyer_avatar": {
    "name": "string",
    "age": "string",
    "gender": "string",
    "education": "string",
    "relationship_family": "string",
    "occupation": "string",
    "income": "string",
    "location": "string"
  },
  "psychographics_lifestyle": {
    "personality_traits": ["string"],
    "hobbies": ["string"],
    "values": ["string"],
    "community_involvement": "string",
    "weekend_routines": "string"
  },
  "pains_challenges": { "narrative": "string", "quotes": ["string"] },
  "fears_relationship_impact": {
    "relationships": {
      "spouse": {"impact": "string", "remarks": ["string"]},
      "kids": {"impact": "string", "remarks": ["string"]},
      "employees": {"impact": "string", "remarks": ["string"]},
      "peers": {"impact": "string", "remarks": ["string"]},
      "clients": {"impact": "string", "remarks": ["string"]}
    }
  },
  "previous_attempts_frustrations": {
    "methods": ["string"],
    "failures": ["string"],
    "quotes": ["string"]
  },
  "desired_outcomes": { "practical": ["string"], "emotional": ["string"], "soundbites": ["string"] },
  "hopes_dreams": { "narrative": "string", "quotes": ["string"] },
  "how_they_want_to_be_seen": { "remarks": ["string"] },
  "unwanted_outcomes": { "narrative": "string", "quotes": ["string"] },
  "summary": "string",
  "day_in_life": [ {"hour": "string", "activity": "string", "outcome": "string"} ]
}`;

function Pill({ children }: { children: React.ReactNode }) {
  return <span className="px-2 py-1 rounded-full bg-gray-100 text-gray-700 text-xs">{children}</span>;
}

// Helper: read files as text
function readFileAsText(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result || ""));
    reader.onerror = reject;
    reader.readAsText(file);
  });
}

export default function App() {
  const [product, setProduct] = useState("SmartFirm Accelerator – done-for-you marketing automation for CPA firms");
  const [notes, setNotes] = useState("Target: US-based accountants/bookkeepers; goal: reduce admin, increase MRR");
  const [view, setView] = useState<'evidence'|'personas'|'prompt'|'uploads'>('evidence');
  const [topic, setTopic] = useState<string | null>(null);

  const [quotes, setQuotes] = useState(MOCK_QUOTES);

  // Bulk upload state
  const [urlsText, setUrlsText] = useState("");
  const [quotesText, setQuotesText] = useState("");
  const [files, setFiles] = useState<FileList | null>(null);
  const [uploadMsg, setUploadMsg] = useState<string>("");

  const filteredQuotes = useMemo(() => {
    if (!topic) return quotes;
    return quotes.filter((q) => (q.topics || []).includes(topic));
  }, [quotes, topic]);

  const exportJSON = () => {
    const data = { product, notes, evidence: quotes, personas: MOCK_PERSONAS };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "audience-research-preview.json";
    a.click();
    URL.revokeObjectURL(url);
  };

  // --- Bulk Upload Actions ---
  const submitUrls = () => {
    const lines = urlsText.split(/\r?\n|,/).map((l) => l.trim()).filter(Boolean);
    if (!lines.length) { setUploadMsg("No URLs provided."); return; }
    const imported = lines.map((u) => ({
      source_type: "link",
      community: "manual",
      published_at: new Date().toISOString().slice(0,10),
      upvotes: 0,
      span: `Imported link: ${u}`,
      url: u,
      stance: "other",
      topics: [],
    }));
    setQuotes((prev) => [...imported, ...prev]);
    setUploadMsg(`Added ${imported.length} URL(s).`);
    setUrlsText("");
  };

  const submitQuotes = () => {
    const lines = quotesText.split(/\r?\n/).map((l) => l.trim()).filter(Boolean);
    if (!lines.length) { setUploadMsg("No quotes provided."); return; }
    const imported = lines.map((text) => ({
      source_type: "manual",
      community: "manual",
      published_at: new Date().toISOString().slice(0,10),
      upvotes: 0,
      span: text,
      url: "",
      stance: "other",
      topics: [],
    }));
    setQuotes((prev) => [...imported, ...prev]);
    setUploadMsg(`Added ${imported.length} quote(s).`);
    setQuotesText("");
  };

  const importFiles = async () => {
    try {
      if (!files || files.length === 0) { setUploadMsg("No files selected."); return; }
      let added = 0;
      for (const f of Array.from(files)) {
        const text = await readFileAsText(f);
        // Expect JSON array of quote objects. CSV not supported in preview.
        try {
          const data = JSON.parse(text);
          if (Array.isArray(data)) {
            const normalized = data.map((r: any) => ({
              source_type: String(r.source_type || "import"),
              community: String(r.community || "import"),
              published_at: String(r.published_at || new Date().toISOString().slice(0,10)),
              upvotes: Number(r.upvotes || 0),
              span: String(r.span || r.text || "(no text)"),
              url: String(r.url || ""),
              stance: String(r.stance || "other"),
              topics: Array.isArray(r.topics) ? r.topics : [],
            }));
            setQuotes((prev) => [...normalized, ...prev]);
            added += normalized.length;
          } else {
            // Not an array
            continue;
          }
        } catch (e) {
          // Not JSON; skip for preview
          continue;
        }
      }
      setUploadMsg(added ? `Imported ${added} record(s) from file(s).` : "No valid JSON arrays found in files.");
      setFiles(null);
    } catch (e:any) {
      setUploadMsg(`Import failed: ${e?.message || e}`);
    }
  };

  return (
    <div className="min-h-screen bg-white text-gray-900 p-6 md:p-10">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between gap-3 flex-wrap">
          <div>
            <h1 className="text-3xl font-semibold tracking-tight">Audience Research Module (Preview)</h1>
            <p className="text-sm text-gray-500 mt-1">Dependency-light build. Bulk upload submit buttons included.</p>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={()=> setView('evidence')} className={`px-3 py-2 rounded-xl border ${view==='evidence'?'bg-gray-900 text-white':'bg-white'}`}>Evidence</button>
            <button onClick={()=> setView('personas')} className={`px-3 py-2 rounded-xl border ${view==='personas'?'bg-gray-900 text-white':'bg-white'}`}>Personas</button>
            <button onClick={()=> setView('prompt')} className={`px-3 py-2 rounded-xl border ${view==='prompt'?'bg-gray-900 text-white':'bg-white'}`}>Prompt & Schema</button>
            <button onClick={()=> setView('uploads')} className={`px-3 py-2 rounded-xl border ${view==='uploads'?'bg-gray-900 text-white':'bg-white'}`}>Bulk Uploads</button>
            <button onClick={exportJSON} className="px-3 py-2 rounded-xl border">Export JSON</button>
          </div>
        </div>

        {/* Inputs */}
        <div className="rounded-2xl border p-4 space-y-4">
          <div className="grid md:grid-cols-2 gap-4">
            <label className="text-sm">Product
              <input className="mt-1 w-full border rounded-xl p-2" value={product} onChange={(e)=> setProduct(e.target.value)} />
            </label>
            <label className="text-sm">Audience Notes
              <input className="mt-1 w-full border rounded-xl p-2" value={notes} onChange={(e)=> setNotes(e.target.value)} />
            </label>
          </div>
          <div className="grid md:grid-cols-4 gap-4">
            <label className="text-sm">Focus Topic
              <select className="mt-1 w-full border rounded-xl p-2" onChange={(e)=> setTopic(e.target.value==='all'?null:e.target.value)}>
                <option value="all">All topics</option>
                <option value="timesheets">timesheets</option>
                <option value="migration">migration</option>
                <option value="billing">billing</option>
                <option value="milestones">milestones</option>
                <option value="handoff">handoff</option>
                <option value="crm">crm</option>
              </select>
            </label>
          </div>
        </div>

        {/* Evidence View */}
        {view === 'evidence' && (
          <div className="space-y-3">
            {filteredQuotes.map((q, idx) => (
              <div key={idx} className="rounded-2xl border p-5 space-y-3">
                <div className="flex items-center gap-2 text-xs text-gray-500 flex-wrap">
                  <Pill>{q.source_type}</Pill>
                  <Pill>{q.community}</Pill>
                  <Pill>{q.published_at}</Pill>
                  <Pill>{q.upvotes} upvotes</Pill>
                  <Pill>{q.stance}</Pill>
                  {(q.topics||[]).map((t)=> <Pill key={t}>{t}</Pill>)}
                </div>
                <p className="text-sm leading-relaxed">“{q.span}”</p>
                {q.url && (
                  <a href={q.url} target="_blank" className="inline-flex items-center gap-1 text-sm text-teal-700 underline">
                    View thread ↗
                  </a>
                )}
              </div>
            ))}
            {filteredQuotes.length === 0 && (
              <p className="text-sm text-gray-500">No quotes for this topic yet.</p>
            )}
          </div>
        )}

        {/* Personas View */}
        {view === 'personas' && (
          <div className="grid md-grid-cols-2 md:grid-cols-2 gap-4">
            {MOCK_PERSONAS.map((p, i) => (
              <div key={i} className="rounded-2xl border p-6 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-xl font-semibold">{p.label}</h3>
                  <div className="flex gap-2 text-xs">
                    <Pill>Risk: {p.risk_tolerance}</Pill>
                    <Pill>{p.sophistication}</Pill>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div>
                    <p><strong>Age:</strong> {p.demographics.age}</p>
                    <p><strong>Gender:</strong> {p.demographics.gender}</p>
                    <p><strong>Location:</strong> {p.demographics.location}</p>
                  </div>
                  <div>
                    <p><strong>Education:</strong> {p.demographics.education}</p>
                    <p><strong>Income:</strong> {p.demographics.income}</p>
                  </div>
                </div>
                <div className="space-y-1 text-sm">
                  <p><strong>Values:</strong> {p.psychographics.values.join(", ")}</p>
                  <p><strong>Interests:</strong> {p.psychographics.interests.join(", ")}</p>
                  <p><strong>Personality:</strong> {p.psychographics.personality}</p>
                </div>
                <div className="text-sm bg-gray-50 rounded-xl p-3">
                  <p className="text-gray-700"><strong>Narrative:</strong> {p.narrative}</p>
                </div>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div>
                    <p><strong>Home life:</strong> {p.psychographics.lifestyle.home_life}</p>
                    <p><strong>Work life:</strong> {p.psychographics.lifestyle.work_life}</p>
                    <p><strong>Family:</strong> {p.psychographics.lifestyle.family}</p>
                  </div>
                  <div>
                    <p><strong>Hobbies:</strong> {p.psychographics.lifestyle.hobbies.join(", ")}</p>
                    <p><strong>Community:</strong> {p.psychographics.lifestyle.community}</p>
                  </div>
                </div>
                <div className="grid md:grid-cols-2 gap-3">
                  <div>
                    <p className="text-sm font-semibold">Jobs To Be Done</p>
                    <ul className="list-disc pl-5 text-sm space-y-1">
                      {p.jobs_to_be_done.map((j, idx) => <li key={idx}>{j}</li>)}
                    </ul>
                  </div>
                  <div>
                    <p className="text-sm font-semibold">Goals</p>
                    <ul className="list-disc pl-5 text-sm space-y-1">
                      {p.goals.map((g, idx) => <li key={idx}>{g}</li>)}
                    </ul>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Prompt & Schema View */}
        {view === 'prompt' && (
          <div className="space-y-4">
            <div className="rounded-2xl border p-4">
              <h3 className="font-semibold mb-2">Prompt Template</h3>
              <textarea readOnly value={PROMPT_TEMPLATE} className="w-full h-56 border rounded-xl p-3 text-sm" />
            </div>
            <div className="rounded-2xl border p-4">
              <h3 className="font-semibold mb-2">JSON Schema</h3>
              <textarea readOnly value={JSON_SCHEMA} className="w-full h-72 border rounded-xl p-3 text-sm" />
            </div>
          </div>
        )}

        {/* Bulk Uploads View */}
        {view === 'uploads' && (
          <div className="space-y-6">
            <div className="rounded-2xl border p-4 space-y-3">
              <h3 className="font-semibold">Paste URLs (one per line)</h3>
              <textarea className="w-full h-28 border rounded-xl p-3 text-sm" value={urlsText} onChange={(e)=> setUrlsText(e.target.value)} placeholder={"https://reddit.com/...\nhttps://www.quora.com/question/..."} />
              <div className="flex gap-2">
                <button onClick={submitUrls} className="px-3 py-2 rounded-xl border bg-gray-900 text-white">Submit URLs</button>
                <button onClick={()=> setUrlsText("")} className="px-3 py-2 rounded-xl border">Clear</button>
              </div>
            </div>

            <div className="rounded-2xl border p-4 space-y-3">
              <h3 className="font-semibold">Paste Quotes (one per line)</h3>
              <textarea className="w-full h-28 border rounded-xl p-3 text-sm" value={quotesText} onChange={(e)=> setQuotesText(e.target.value)} placeholder={"\"We lost a week reconciling timesheets...\"\n\"Handoff between chat and phone is messy...\""} />
              <div className="flex gap-2">
                <button onClick={submitQuotes} className="px-3 py-2 rounded-xl border bg-gray-900 text-white">Submit Quotes</button>
                <button onClick={()=> setQuotesText("")} className="px-3 py-2 rounded-xl border">Clear</button>
              </div>
            </div>

            <div className="rounded-2xl border p-4 space-y-3">
              <h3 className="font-semibold">Upload JSON File(s)</h3>
              <input type="file" multiple accept="application/json" onChange={(e)=> setFiles(e.target.files)} className="block" />
              <div className="flex gap-2">
                <button onClick={importFiles} className="px-3 py-2 rounded-xl border bg-gray-900 text-white">Import File(s)</button>
                <button onClick={()=> { setFiles(null); const inp = document.querySelector('input[type=file]') as HTMLInputElement; if (inp) inp.value=''; }} className="px-3 py-2 rounded-xl border">Clear Selection</button>
              </div>
              <p className="text-xs text-gray-500">Preview supports JSON arrays of quote objects. CSV is not supported in the preview but can be handled in your backend.</p>
            </div>

            {uploadMsg && <p className="text-sm text-teal-700">{uploadMsg}</p>}
          </div>
        )}
      </div>
    </div>
  );
}
