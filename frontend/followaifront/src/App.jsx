import { useState } from "react";
import "./App.css";
import { mascotImg, laptopGirlImg, headphonesBoyImg, heroMascotImg } from "./assets";

const API_BASE_URL = `${import.meta.env.VITE_API_URL || 
  "http://127.0.0.1:8000"}/api/v1/conversations`;
/* 
   ICONS (inline SVG, no external deps)
 */
const IconMic = (p) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" {...p}>
    <rect x="9" y="2" width="6" height="12" rx="3" />
    <path d="M5 10a7 7 0 0 0 14 0" />
    <path d="M12 19v3M8 22h8" />
  </svg>
);

const IconMail = (p) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" {...p}>
    <rect x="3" y="5" width="18" height="14" rx="2" />
    <path d="m3 7 9 6 9-6" />
  </svg>
);

const IconUpload = (p) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" {...p}>
    <path d="M12 16V4M7 9l5-5 5 5" />
    <path d="M4 16v3a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-3" />
  </svg>
);

const IconSparkle = (p) => (
  <svg viewBox="0 0 24 24" fill="currentColor" {...p}>
    <path d="M12 2l1.8 5.6L19 9l-5.2 1.4L12 16l-1.8-5.6L5 9l5.2-1.4L12 2z" />
  </svg>
);

const IconTarget = (p) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" {...p}>
    <circle cx="12" cy="12" r="9" />
    <circle cx="12" cy="12" r="5" />
    <circle cx="12" cy="12" r="1" />
  </svg>
);

const IconBolt = (p) => (
  <svg viewBox="0 0 24 24" fill="currentColor" {...p}>
    <path d="M13 2 4 14h6l-1 8 9-12h-6l1-8z" />
  </svg>
);

const IconShield = (p) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" {...p}>
    <path d="M12 2 4 5v6c0 5 3.5 8.5 8 11 4.5-2.5 8-6 8-11V5l-8-3z" />
    <path d="m9 12 2 2 4-4" />
  </svg>
);

const IconCheck = (p) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" {...p}>
    <path d="M20 6 9 17l-5-5" />
  </svg>
);

const IconEdit = (p) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" {...p}>
    <path d="M12 20h9" />
    <path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" />
  </svg>
);

const IconX = (p) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" {...p}>
    <path d="M18 6 6 18M6 6l12 12" />
  </svg>
);

const IconClock = (p) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" {...p}>
    <circle cx="12" cy="12" r="9" />
    <path d="M12 7v5l3 3" />
  </svg>
);

const IconCheckDot = (p) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" {...p}>
    <circle cx="12" cy="12" r="9" fill="var(--green-100)" stroke="none" />
    <path d="m8 12.5 2.5 2.5L16 9.5" stroke="var(--green-500)" />
  </svg>
);

/* 
   SCORE DIAL
 */
function ScoreDial({ score }) {
  const value = Math.min(Math.max(Number(score) || 0, 0), 100);
  const radius = 52;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (circumference * value) / 100;

  return (
    <div className="score-dial">
      <svg viewBox="0 0 120 120">
        <circle className="dial-track" cx="60" cy="60" r={radius} />
        <circle
          className="dial-fill"
          cx="60"
          cy="60"
          r={radius}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
        />
      </svg>
      <div className="dial-label">{score ?? "-"}</div>
    </div>
  );
}

/* 
   CONVERSATION INTELLIGENCE CARD
*/
function ConversationIntelligenceCard({ data }) {
  if (!data || typeof data !== "object") return null;

  const needs = Array.isArray(data.customer_needs) ? data.customer_needs : [];
  const painPoints = Array.isArray(data.pain_points) ? data.pain_points : [];
  const requirements = Array.isArray(data.requirements) ? data.requirements : [];
  const signals = Array.isArray(data.buying_signals) ? data.buying_signals : [];

  const hasKnownShape =
    data.customer_intent || needs.length || requirements.length ||
    signals.length || data.summary || data.decision_timeline;

  if (!hasKnownShape) {
    return <pre>{JSON.stringify(data, null, 2)}</pre>;
  }

  return (
    <div className="insight-card">
      <img src={laptopGirlImg} alt="" className="insight-avatar" />

      <div className="insight-body">
        {data.customer_intent && (
          <div className="insight-intent">
            <span className="insight-eyebrow">Customer intent</span>
            <p>{data.customer_intent}</p>
          </div>
        )}

        <div className="insight-row">
          {needs.length > 0 && (
            <div className="insight-group">
              <span className="insight-label">Needs</span>
              <div className="chip-row">
                {needs.map((n, i) => (
                  <span key={i} className="chip chip-blue">{n}</span>
                ))}
              </div>
            </div>
          )}

          {requirements.length > 0 && (
            <div className="insight-group">
              <span className="insight-label">Requirements</span>
              <div className="chip-row">
                {requirements.map((r, i) => (
                  <span key={i} className="chip chip-orange">{r}</span>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="insight-group">
          <span className="insight-label">Pain points</span>
          <div className="chip-row">
            {painPoints.length > 0 ? (
              painPoints.map((p, i) => (
                <span key={i} className="chip chip-red">{p}</span>
              ))
            ) : (
              <span className="chip chip-green">None flagged</span>
            )}
          </div>
        </div>

        {signals.length > 0 && (
          <div className="insight-group">
            <span className="insight-label">Buying signals</span>
            <ul className="signal-list">
              {signals.map((s, i) => (
                <li key={i}>
                  <IconCheckDot width="18" height="18" />
                  {s}
                </li>
              ))}
            </ul>
          </div>
        )}

        {data.decision_timeline && (
          <span className="timeline-badge">
            <IconClock width="14" height="14" />
            Decision expected: {data.decision_timeline}
          </span>
        )}

        {data.summary && <p className="insight-summary">{data.summary}</p>}
      </div>
    </div>
  );
}

/* 
   NEXT BEST ACTION CARD
*/
function NextBestActionCard({ data }) {
  if (!data || typeof data !== "object") return null;

  const hasKnownShape = data.action || data.reason || data.urgency;
  if (!hasKnownShape) {
    return <pre>{JSON.stringify(data, null, 2)}</pre>;
  }

  const urgency = (data.urgency || "").toLowerCase();

  return (
    <div className="action-card">
      <img src={headphonesBoyImg} alt="" className="action-avatar" />

      <div className="action-body">
        {data.urgency && (
          <span className={`urgency-badge urgency-${urgency}`}>
            <IconBolt width="12" height="12" />
            {data.urgency} urgency
          </span>
        )}

        {data.action && <h4 className="action-title">{data.action}</h4>}
        {data.reason && <p className="action-reason">{data.reason}</p>}
      </div>
    </div>
  );
}

/* 
   FOLLOW-UP CARD
 */
function FollowUpCard({ data }) {
  if (!data || typeof data !== "object") return null;

  const hasKnownShape = data.purpose || data.follow_up_timing || data.urgency;
  if (!hasKnownShape) {
    return <pre>{JSON.stringify(data, null, 2)}</pre>;
  }

  const urgency = (data.urgency || "").toLowerCase();

  return (
    <div className="followup-card">
      <div className="followup-icon">
        <IconClock width="20" height="20" />
      </div>
      <div className="followup-body">
        {data.follow_up_timing && (
          <span className="timeline-badge">
            <IconClock width="14" height="14" />
            {data.follow_up_timing}
          </span>
        )}
        {data.purpose && <p className="followup-purpose">{data.purpose}</p>}
        {data.urgency && (
          <span className={`urgency-badge urgency-${urgency}`}>
            <IconBolt width="12" height="12" />
            {data.urgency} urgency
          </span>
        )}
      </div>
    </div>
  );
}

/* ==================================================
   DASHBOARD (shown after Approve & Send)
================================================== */
function StatCard({ label, value, tone, icon }) {
  return (
    <div className={`stat-card stat-${tone}`}>
      <div className="stat-icon">{icon}</div>
      <div className="stat-text">
        <span>{label}</span>
        <strong>{value}</strong>
      </div>
    </div>
  );
}

function Dashboard({ stats, analysis, onNewAnalysis }) {
  return (
    <div className="dashboard">

      <div className="dashboard-hero">
        <img src={mascotImg} alt="" className="dashboard-mascot" />
        <div>
          <span className="dashboard-eyebrow">
            <IconCheck width="12" height="12" /> Email sent
          </span>
          <h2>Nice work — that follow-up is on its way!</h2>
          <p>Here's how your pipeline looks right now.</p>
        </div>
      </div>

      <div className="stat-grid">
        <StatCard label="Total Leads" value={stats.total} tone="navy" icon={<IconTarget width="20" height="20" />} />
        <StatCard label="Hot Leads" value={stats.hot} tone="red" icon={<IconBolt width="20" height="20" />} />
        <StatCard label="Warm Leads" value={stats.warm} tone="orange" icon={<IconSparkle width="20" height="20" />} />
        <StatCard label="Cold Leads" value={stats.cold} tone="blue" icon={<IconClock width="20" height="20" />} />
      </div>

      {analysis && (
        <>
          <section className="card">
            <h2><IconTarget /> Conversation Intelligence</h2>
            <ConversationIntelligenceCard data={analysis.conversation_analysis} />
          </section>

          <section className="card">
            <h2><IconSparkle /> Lead Scoring Reason</h2>
            <p className="reason-text">
              {analysis.lead_scoring_reason || "No reason available."}
            </p>
          </section>

          <section className="card">
            <h2><IconBolt /> Next Best Action</h2>
            <NextBestActionCard data={analysis.next_best_action} />
          </section>

          <section className="card">
            <h2><IconClock /> Follow-up</h2>
            <FollowUpCard data={analysis.follow_up} />
          </section>
        </>
      )}

      <button className="primary" onClick={onNewAnalysis}>
        <IconMic width="16" height="16" /> Start a New Analysis
      </button>

    </div>
  );
}

function priorityClass(priority) {
  const p = (priority || "").toLowerCase();
  if (p === "hot") return "hot";
  if (p === "warm") return "warm";
  if (p === "cold") return "cold";
  return "default";
}

function App() {
  const [activeTab, setActiveTab] = useState("call");

  const [audioFile, setAudioFile] = useState(null);

  const [emailSubject, setEmailSubject] = useState("");
  const [emailBody, setEmailBody] = useState("");

  const [customerEmail, setCustomerEmail] = useState("");

  const [conversationId, setConversationId] = useState(null);

  const [analysis, setAnalysis] = useState(null);
  const [generatedEmail, setGeneratedEmail] = useState(null);

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const [showDashboard, setShowDashboard] = useState(false);
  const [leadStats, setLeadStats] = useState({
    total: 128,
    hot: 42,
    warm: 51,
    cold: 35,
  });

  
  // CALL ANALYSIS


  const analyzeCall = async () => {
    if (!audioFile) {
      setMessage("Please select an audio file.");
      return;
    }

    setLoading(true);
    setMessage("");

    try {
      const formData = new FormData();

      formData.append("file", audioFile);

      const response = await fetch(
        `${API_BASE_URL}/call`,
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Call analysis failed"
        );
      }

      setConversationId(data.conversation_id);
      setAnalysis(data);
      setGeneratedEmail(null);

      setMessage("Call analyzed successfully.");
    } catch (error) {
      setMessage(
        error.message || "Call analysis failed."
      );
    } finally {
      setLoading(false);
    }
  };

  
  // EMAIL ANALYSIS
 

  const analyzeEmail = async () => {
    if (!emailBody.trim()) {
      setMessage("Please enter the email body.");
      return;
    }

    setLoading(true);
    setMessage("");

    try {
      const response = await fetch(
        `${API_BASE_URL}/email`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email_subject: emailSubject,
            email_body: emailBody,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Email analysis failed"
        );
      }

      setConversationId(data.conversation_id);
      setAnalysis(data);
      setGeneratedEmail(null);

      setMessage(
        "Email conversation analyzed successfully."
      );
    } catch (error) {
      setMessage(
        error.message || "Email analysis failed."
      );
    } finally {
      setLoading(false);
    }
  };

  
  // GENERATE FOLLOW-UP EMAIL
  

  const generateEmail = async () => {
    if (!conversationId) {
      setMessage(
        "Please analyze a conversation first."
      );
      return;
    }

    if (!customerEmail.trim()) {
      setMessage(
        "Please enter customer email."
      );
      return;
    }

    setLoading(true);
    setMessage("");

    try {
      const response = await fetch(
        `${API_BASE_URL}/${conversationId}/generate-email`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            customer_email: customerEmail,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Email generation failed"
        );
      }

      if (!data.email) {
        throw new Error(
          "No email was generated."
        );
      }

      setGeneratedEmail({
        subject: data.email.subject || "",
        body: data.email.body || "",
      });

      setMessage(
        "Follow-up email generated successfully."
      );
    } catch (error) {
      setMessage(
        error.message || "Email generation failed."
      );
    } finally {
      setLoading(false);
    }
  };

  
  // APPROVE & SEND EMAIL
  

  const approveEmail = async () => {
    if (!conversationId) {
      setMessage(
        "Conversation not found."
      );
      return;
    }

    setLoading(true);
    setMessage("");

    try {
      const response = await fetch(
        `${API_BASE_URL}/${conversationId}/approve`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            action: "approve",
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Email sending failed."
        );
      }

      // Update frontend with the email actually sent
      if (data.email) {
        setGeneratedEmail({
          subject: data.email.subject || "",
          body: data.email.body || "",
        });
      }

      // Bump the (demo) lead dashboard stats based on this lead's priority
      const priority = (analysis?.lead_priority || "").toLowerCase();
      setLeadStats((prev) => ({
        total: prev.total + 1,
        hot: prev.hot + (priority === "hot" ? 1 : 0),
        warm: prev.warm + (priority === "warm" ? 1 : 0),
        cold: prev.cold + (priority === "cold" ? 1 : 0),
      }));

      setMessage(
        "Email sent successfully!"
      );
      setShowDashboard(true);
    } catch (error) {
      setMessage(
        error.message || "Email sending failed."
      );
    } finally {
      setLoading(false);
    }
  };

  

  const saveEdit = async () => {
    if (!conversationId) {
      setMessage(
        "Conversation not found."
      );
      return;
    }

    if (!generatedEmail) {
      setMessage(
        "No email available to edit."
      );
      return;
    }

    if (!generatedEmail.subject.trim()) {
      setMessage(
        "Email subject cannot be empty."
      );
      return;
    }

    if (!generatedEmail.body.trim()) {
      setMessage(
        "Email body cannot be empty."
      );
      return;
    }

    setLoading(true);
    setMessage("");

    try {
      const response = await fetch(
        `${API_BASE_URL}/${conversationId}/edit`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            subject: generatedEmail.subject,
            body: generatedEmail.body,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Email edit failed."
        );
      }

      // IMPORTANT:
      // Keep the edited email in React state.
      // It has NOT been sent yet.
      if (data.email) {
        setGeneratedEmail({
          subject: data.email.subject || "",
          body: data.email.body || "",
        });
      }

      setMessage(
        "✏️ Email edited and saved. Click Approve & Send to send it."
      );
    } catch (error) {
      setMessage(
        error.message || "Email edit failed."
      );
    } finally {
      setLoading(false);
    }
  };


  // REJECT EMAIL
 

  const rejectEmail = async () => {
    if (!conversationId) {
      setMessage(
        "Conversation not found."
      );
      return;
    }

    setLoading(true);
    setMessage("");

    try {
      const response = await fetch(
        `${API_BASE_URL}/${conversationId}/reject`,
        {
          method: "POST",
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Email rejection failed."
        );
      }

      setGeneratedEmail(null);

      setMessage(
        "❌ Email rejected. It was not sent."
      );
    } catch (error) {
      setMessage(
        error.message || "Email rejection failed."
      );
    } finally {
      setLoading(false);
    }
  };


  // RESET FOR NEW ANALYSIS


  const startNewAnalysis = () => {
    setShowDashboard(false);
    setAnalysis(null);
    setGeneratedEmail(null);
    setConversationId(null);
    setAudioFile(null);
    setEmailSubject("");
    setEmailBody("");
    setCustomerEmail("");
    setMessage("");
  };

  
  // RENDER
 

  return (
    <div className="app">

      {/* 
          HEADER
       */}

      <header className="header">
        <div className="header-inner">
          <div className="header-text">
            <span className="eyebrow">
              <IconSparkle width="12" height="12" /> AI Sales Copilot
            </span>
            <h1>Follow<span>AI</span></h1>
            <p>Turns every call and email into a scored lead and a ready-to-send follow-up.</p>
          </div>
          <img src={heroMascotImg} alt="" className="mascot" />
        </div>
      </header>

      <main className="container">

        {showDashboard ? (

          <Dashboard
            stats={leadStats}
            analysis={analysis}
            onNewAnalysis={startNewAnalysis}
          />

        ) : (
        <>

        {/* 
            TABS
        */}

        <div className="tabs">

          <button
            className={
              activeTab === "call"
                ? "active"
                : ""
            }
            onClick={() => {
              setActiveTab("call");
              setMessage("");
            }}
          >
            <IconMic /> Call Conversation
          </button>

          <button
            className={
              activeTab === "email"
                ? "active"
                : ""
            }
            onClick={() => {
              setActiveTab("email");
              setMessage("");
            }}
          >
            <IconMail /> Email Conversation
          </button>

        </div>

        {/* 
            INPUT SECTION
         */}

        <section className="card">

          <h2>
            {activeTab === "call" ? <IconMic /> : <IconMail />}
            {activeTab === "call"
              ? "Analyze Call"
              : "Analyze Email Conversation"}
          </h2>

          {activeTab === "call" ? (

            <div>

              <label className="file-drop">
                <input
                  type="file"
                  accept=".mp3,.wav,.m4a,.mp4,.webm,.ogg"
                  onChange={(e) =>
                    setAudioFile(
                      e.target.files[0]
                    )
                  }
                />
                <span className="drop-icon">
                  <IconUpload width="20" height="20" />
                </span>
                <span className="drop-text">
                  <strong>{audioFile ? audioFile.name : "Choose a call recording"}</strong>
                  <span>MP3, WAV, M4A, MP4, WEBM or OGG</span>
                </span>
              </label>

              <button
                className="primary"
                onClick={analyzeCall}
                disabled={loading}
              >
                <IconBolt width="16" height="16" />
                {loading
                  ? "Analyzing..."
                  : "Analyze Call"}
              </button>

            </div>

          ) : (

            <div className="email-input">

              <input
                type="text"
                placeholder="Email subject"
                value={emailSubject}
                onChange={(e) =>
                  setEmailSubject(
                    e.target.value
                  )
                }
              />

              <textarea
                placeholder="Paste customer email here..."
                value={emailBody}
                onChange={(e) =>
                  setEmailBody(
                    e.target.value
                  )
                }
              />

              <button
                className="primary"
                onClick={analyzeEmail}
                disabled={loading}
              >
                <IconBolt width="16" height="16" />
                {loading
                  ? "Analyzing..."
                  : "Analyze Email"}
              </button>

            </div>

          )}

        </section>

        {/* 
            MESSAGE
        */}

        {message && (
          <div className="message">
            <IconSparkle width="16" height="16" />
            {message}
          </div>
        )}

        {/* 
            AI ANALYSIS
         */}

        {analysis && (

          <section className="card">

            <h2>
              <IconTarget /> AI Conversation Analysis
            </h2>

            <div className="grid">

              <div className="metric">
                <ScoreDial score={analysis.lead_score} />
                <div className="metric-text">
                  <span>Lead Score</span>
                  <strong>{analysis.lead_score ?? "-"} / 100</strong>
                </div>
              </div>

              <div className="metric">
                <div className="metric-text">
                  <span>Lead Priority</span>
                  <span className={`priority-pill ${priorityClass(analysis.lead_priority)}`}>
                    {analysis.lead_priority ?? "-"}
                  </span>
                </div>
              </div>

            </div>

            <div className="result-block">

              <h3>
                Conversation Intelligence
              </h3>

              <ConversationIntelligenceCard data={analysis.conversation_analysis} />

            </div>

            <div className="result-block">

              <h3>
                Lead Scoring Reason
              </h3>

              <p>
                {analysis.lead_scoring_reason ||
                  "No reason available."}
              </p>

            </div>

            <div className="result-block">

              <h3>
                Next Best Action
              </h3>

              <NextBestActionCard data={analysis.next_best_action} />

            </div>

            <div className="result-block">

              <h3>
                Follow-up
              </h3>

              <FollowUpCard data={analysis.follow_up} />

            </div>

          </section>

        )}

        {/* 
            CUSTOMER EMAIL
         */}

        {analysis && !generatedEmail && (

          <section className="card">

            <h2>
              <IconMail /> Generate Follow-up Email
            </h2>

            <p>
              Enter the customer's email address.
            </p>

            <input
              type="email"
              placeholder="customer@example.com"
              value={customerEmail}
              onChange={(e) =>
                setCustomerEmail(
                  e.target.value
                )
              }
            />

            <button
              className="primary"
              onClick={generateEmail}
              disabled={loading}
            >
              <IconSparkle width="16" height="16" />
              {loading
                ? "Generating..."
                : "Generate Follow-up Email"}
            </button>

          </section>

        )}

        {/* 
            GENERATED / EDITABLE EMAIL
        */}

        {generatedEmail && (

          <section className="card">

            <h2>
              <IconMail /> Follow-up Email
            </h2>

            <label>
              Subject
            </label>

            <input
              type="text"
              value={
                generatedEmail.subject
              }
              onChange={(e) =>
                setGeneratedEmail({
                  ...generatedEmail,
                  subject: e.target.value,
                })
              }
              disabled={loading}
            />

            <label>
              Body
            </label>

            <textarea
              className="email-editor"
              value={
                generatedEmail.body
              }
              onChange={(e) =>
                setGeneratedEmail({
                  ...generatedEmail,
                  body: e.target.value,
                })
              }
              disabled={loading}
            />

            {/* 
                ACTIONS
             */}

            <div className="actions">

              {/* APPROVE & SEND */}

              <button
                className="approve"
                onClick={approveEmail}
                disabled={loading}
              >
                <IconCheck width="15" height="15" />
                {loading
                  ? "Sending..."
                  : "Approve & Send"}
              </button>

              {/* SAVE EDIT ONLY */}

              <button
                className="edit"
                onClick={saveEdit}
                disabled={loading}
              >
                <IconEdit width="15" height="15" />
                {loading
                  ? "Saving..."
                  : "Save Edit"}
              </button>

              {/* REJECT */}

              <button
                className="reject"
                onClick={rejectEmail}
                disabled={loading}
              >
                <IconX width="15" height="15" />
                Reject
              </button>

            </div>

            {/* INFO */}

            <p className="email-status">
              Edit the email and click{" "}
              <strong>
                Save Edit
              </strong>{" "}
              to save your changes.
              <br />
              Then click{" "}
              <strong>
                Approve & Send
              </strong>{" "}
              to send the latest version.
            </p>

          </section>

        )}

        {/* 
            FEATURE STRIP
         */}

        <div className="feature-strip">
          <div className="feature-chip">
            <IconSparkle />
            <strong>AI-Powered</strong>
            <span>Reads tone, intent & context</span>
          </div>
          <div className="feature-chip">
            <IconTarget />
            <strong>Smart Scoring</strong>
            <span>Prioritizes hot leads first</span>
          </div>
          <div className="feature-chip">
            <IconBolt />
            <strong>Automated Follow-ups</strong>
            <span>Drafts emails that convert</span>
          </div>
          <div className="feature-chip">
            <IconShield />
            <strong>Secure & Private</strong>
            <span>Your conversations stay yours</span>
          </div>
        </div>

        </>
        )}

      </main>

    </div>
  );
}

export default App;
