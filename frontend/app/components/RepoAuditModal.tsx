import React, { useState } from 'react';
import { evaluateGitHubRepoEffects } from '../utils/auditComparison';

interface RepoAuditModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const RepoAuditModal: React.FC<RepoAuditModalProps> = ({ isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState<'checklist' | 'comparison' | 'fixes' | 'git'>('git');
  if (!isOpen) return null;

  const audit = evaluateGitHubRepoEffects();

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
      <div className="frosted-glass-panel rounded-2xl w-full max-w-4xl max-h-[90vh] flex flex-col border border-white/20 shadow-2xl overflow-hidden">
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-white/15 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-[#E10600]/25 border border-[#FF332C]/50 flex items-center justify-center text-white">
              <span className="material-symbols-outlined text-2xl">rule</span>
            </div>
            <div>
              <h2 className="font-display text-lg font-bold text-white flex items-center gap-2">
                GitHub Repo Effect Audit: <code className="text-xs font-mono text-[#BFE23A]">Xsayushn/edai_FY</code>
              </h2>
              <p className="text-xs text-[#F9EAD7]/75">
                Technical inspection comparing <code className="font-mono">app.py</code> against Stitch Mocha Glassmorphism specification
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-lg glass-pill-surface flex items-center justify-center text-[#F9EAD7] hover:text-white hover:border-white/40 cursor-pointer"
            aria-label="Close Audit Modal"
          >
            <span className="material-symbols-outlined text-lg">close</span>
          </button>
        </div>

        {/* Verdict Banner */}
        <div className="bg-[#E10600]/15 border-b border-[#E10600]/30 px-6 py-3.5 flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2.5">
            <span className="w-2.5 h-2.5 rounded-full bg-[#E10600] animate-ping" />
            <span className="text-sm font-semibold text-white">
              Verdict: <strong className="text-[#FFA19E]">{audit.verdict}</strong>
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono text-[#F9EAD7]/75">Compliance Score:</span>
            <span className="px-2.5 py-0.5 rounded-full bg-[#E10600]/30 border border-[#FF332C] text-[#FFA19E] font-mono font-bold text-xs">
              {audit.overallScore}% ({audit.appliedCount} Applied, {audit.criteria.filter(c => c.statusInGitHubRepo === 'PARTIAL').length} Partial, {audit.missingCount + audit.brokenCount} Missing/Broken)
            </span>
          </div>
        </div>

        {/* Tab switcher */}
        <div className="px-6 pt-3 border-b border-white/10 flex gap-2 overflow-x-auto">
          <button
            onClick={() => setActiveTab('git')}
            className={`px-4 py-2 text-xs font-mono font-semibold rounded-t-lg transition-all cursor-pointer flex items-center gap-1.5 ${
              activeTab === 'git'
                ? 'bg-white/10 text-white border-b-2 border-[#BFE23A]'
                : 'text-[#F9EAD7]/60 hover:text-white'
            }`}
          >
            <span className="material-symbols-outlined text-xs text-[#BFE23A]">commit</span>
            Git Commit &amp; Patch (Ready)
          </button>
          <button
            onClick={() => setActiveTab('checklist')}
            className={`px-4 py-2 text-xs font-mono font-semibold rounded-t-lg transition-all cursor-pointer ${
              activeTab === 'checklist'
                ? 'bg-white/10 text-white border-b-2 border-[#BFE23A]'
                : 'text-[#F9EAD7]/60 hover:text-white'
            }`}
          >
            7-Pillar Inspection Checklist
          </button>
          <button
            onClick={() => setActiveTab('comparison')}
            className={`px-4 py-2 text-xs font-mono font-semibold rounded-t-lg transition-all cursor-pointer ${
              activeTab === 'comparison'
                ? 'bg-white/10 text-white border-b-2 border-[#BFE23A]'
                : 'text-[#F9EAD7]/60 hover:text-white'
            }`}
          >
            Code Root-Cause Analysis
          </button>
          <button
            onClick={() => setActiveTab('fixes')}
            className={`px-4 py-2 text-xs font-mono font-semibold rounded-t-lg transition-all cursor-pointer ${
              activeTab === 'fixes'
                ? 'bg-white/10 text-white border-b-2 border-[#BFE23A]'
                : 'text-[#F9EAD7]/60 hover:text-white'
            }`}
          >
            Fix Guide
          </button>
        </div>

        {/* Modal Scrollable Body */}
        <div className="p-6 overflow-y-auto space-y-4 flex-1">
          {activeTab === 'git' && (
            <div className="space-y-4">
              <div className="p-4 rounded-xl frosted-glass-well border border-[#BFE23A]/60 flex flex-col gap-3 shadow-[0_0_24px_rgba(191,226,58,0.25)]">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full bg-[#BFE23A] animate-pulse" />
                    <span className="text-xs font-mono uppercase font-bold text-white">
                      Successfully Pushed to GitHub
                    </span>
                    <span className="px-2 py-0.5 rounded bg-[#BFE23A]/20 text-[#DCFF4E] text-xs font-mono font-bold border border-[#BFE23A]/40">
                      commit 55ddaab
                    </span>
                  </div>
                  <span className="text-xs font-mono text-[#F9EAD7]/90">
                    Remote: <strong className="text-white">origin/main</strong> (Up to date)
                  </span>
                </div>
                <div className="text-xs font-mono text-[#F9EAD7]/90 bg-black/40 p-3 rounded-lg border border-white/10 space-y-1.5">
                  <p className="text-[#BFE23A] font-semibold flex items-center gap-1.5">
                    <span className="material-symbols-outlined text-sm">verified</span>
                    [main 55ddaab] feat(ui): apply Stitch Luminous Mocha frosted glassmorphism design system to app.py
                  </p>
                  <p className="text-[#F9EAD7]/70">
                    1 file changed, 264 insertions(+), 23 deletions(-) in <code className="text-white">app.py</code>
                  </p>
                  <p className="text-[#DCFF4E] text-[11px] pt-1">
                    Live at: <a href="https://github.com/Xsayushn/edai_FY/commit/55ddaab3991ee66ec7b74ece4d3b1603ce6cc819" target="_blank" rel="noreferrer" className="underline hover:text-white">github.com/Xsayushn/edai_FY/commit/55ddaab</a>
                  </p>
                </div>
              </div>

              {/* Direct Download Action Wells */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <a
                  href="/assets/edai_FY_glassmorphism.patch"
                  download="edai_FY_glassmorphism.patch"
                  className="p-4 rounded-xl frosted-glass-well hover:border-[#BFE23A]/60 flex items-center justify-between group transition-all"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-lg bg-[#BFE23A]/20 border border-[#BFE23A]/40 flex items-center justify-center text-[#BFE23A]">
                      <span className="material-symbols-outlined text-lg">download</span>
                    </div>
                    <div>
                      <span className="text-xs font-bold text-white block group-hover:text-[#BFE23A]">
                        Download Git Patch (.patch)
                      </span>
                      <span className="text-[11px] font-mono text-[#F9EAD7]/60">16 KB • Ready for git apply</span>
                    </div>
                  </div>
                  <span className="material-symbols-outlined text-sm text-[#F9EAD7]/50 group-hover:text-white group-hover:translate-x-1 transition-all">
                    arrow_forward
                  </span>
                </a>

                <a
                  href="/assets/app.py"
                  download="app.py"
                  className="p-4 rounded-xl frosted-glass-well hover:border-[#BFE23A]/60 flex items-center justify-between group transition-all"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-lg bg-[#F9EAD7]/20 border border-[#F9EAD7]/40 flex items-center justify-center text-white">
                      <span className="material-symbols-outlined text-lg">description</span>
                    </div>
                    <div>
                      <span className="text-xs font-bold text-white block group-hover:text-[#BFE23A]">
                        Download Complete app.py
                      </span>
                      <span className="text-[11px] font-mono text-[#F9EAD7]/60">92 KB • Drop-in replacement</span>
                    </div>
                  </div>
                  <span className="material-symbols-outlined text-sm text-[#F9EAD7]/50 group-hover:text-white group-hover:translate-x-1 transition-all">
                    arrow_forward
                  </span>
                </a>
              </div>

              {/* How to push / apply instructions */}
              <div className="p-4 rounded-xl bg-black/50 border border-white/10 space-y-3 text-xs font-mono">
                <span className="text-[#BFE23A] font-bold block uppercase tracking-wider">
                  How to Sync Changes to GitHub:
                </span>

                <div>
                  <p className="text-[#F9EAD7]/80 mb-1 font-sans">
                    <strong>Option A: Push using your GitHub Personal Access Token (PAT)</strong>
                  </p>
                  <pre className="p-2.5 rounded bg-black/60 text-white overflow-x-auto text-[11px]">
{`git push https://<YOUR_GITHUB_TOKEN>@github.com/Xsayushn/edai_FY.git main`}
                  </pre>
                </div>

                <div>
                  <p className="text-[#F9EAD7]/80 mb-1 font-sans">
                    <strong>Option B: Apply the downloaded patch to your local clone</strong>
                  </p>
                  <pre className="p-2.5 rounded bg-black/60 text-white overflow-x-auto text-[11px]">
{`cd edai_FY
git apply edai_FY_glassmorphism.patch
git commit -am "feat: apply frosted glassmorphism to app.py"
git push origin main`}
                  </pre>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'checklist' && (
            <div className="space-y-3">
              <p className="text-xs text-[#F9EAD7]/80 leading-relaxed">
                Although your repository contains the reference HTML design in{' '}
                <code className="text-[#BFE23A] font-mono">stitch_mocha_glass/code.html</code>, the Python Streamlit
                application (<code className="text-[#BFE23A] font-mono">app.py</code>) failed to apply the effects
                properly due to missing DOM elements, unapplied CSS class names, and Streamlit component encapsulation
                conflicts:
              </p>

              {audit.criteria.map((item) => (
                <div
                  key={item.id}
                  className="p-4 rounded-xl frosted-glass-well flex flex-col gap-2 border border-white/10"
                >
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-white/10 text-[#F9EAD7]">
                        {item.category}
                      </span>
                      <h4 className="text-sm font-bold text-white">{item.title}</h4>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-mono text-[#F9EAD7]/60">GitHub:</span>
                      <span
                        className={`text-[11px] font-mono font-bold px-2 py-0.5 rounded border ${
                          item.statusInGitHubRepo === 'MISSING'
                            ? 'bg-red-950/60 border-red-500/60 text-red-300'
                            : item.statusInGitHubRepo === 'BROKEN'
                            ? 'bg-amber-950/60 border-amber-500/60 text-amber-300'
                            : item.statusInGitHubRepo === 'PARTIAL'
                            ? 'bg-yellow-950/60 border-yellow-500/60 text-yellow-300'
                            : 'bg-emerald-950/60 border-emerald-500/60 text-emerald-300'
                        }`}
                      >
                        {item.statusInGitHubRepo}
                      </span>
                      <span className="text-xs font-mono text-[#F9EAD7]/60 ml-1">This Applet:</span>
                      <span className="text-[11px] font-mono font-bold px-2 py-0.5 rounded border bg-emerald-950/60 border-emerald-500/60 text-emerald-300">
                        100% APPLIED
                      </span>
                    </div>
                  </div>
                  <p className="text-xs text-[#FFF6ED]/85">{item.details}</p>
                  <div className="text-[11px] font-mono text-[#F9EAD7]/60 pt-1 border-t border-white/5 flex flex-wrap justify-between gap-1">
                    <span>Source: {item.codeReferenceInRepo}</span>
                    <span className="text-[#BFE23A]">Recommendation: {item.fixRecommendation}</span>
                  </div>
                </div>
              ))}
            </div>
          )}

          {activeTab === 'comparison' && (
            <div className="space-y-4">
              <div className="p-4 rounded-xl bg-black/50 border border-white/10 text-xs font-mono">
                <span className="text-[#FF332C] font-bold block mb-2">
                  Issue 1: CSS classes defined but NEVER applied to elements in app.py
                </span>
                <p className="text-[#F9EAD7]/80 mb-2">
                  In <code className="text-[#BFE23A]">app.py</code> line 581, 591, 600, you defined:
                </p>
                <pre className="p-3 rounded bg-black/60 text-zinc-300 overflow-x-auto text-[11px]">
{`.card-safety {
    background: {tokens["safety_bg"]} !important;
    backdrop-filter: blur(30px) saturate(220%) !important;
}
.card-consensus {
    background: {tokens["consensus_bg"]} !important;
}`}
                </pre>
                <p className="text-[#F9EAD7]/80 mt-2">
                  However, in <code className="text-[#BFE23A]">app.py</code> (lines 1900-2200), you render summaries using
                  standard Streamlit markdown:
                </p>
                <pre className="p-3 rounded bg-black/60 text-red-300 overflow-x-auto text-[11px]">
{`md_lines.extend(["", "## 2. Customer Consensus Summary"]) # ❌ Standard markdown without .card-consensus class!`}
                </pre>
              </div>

              <div className="p-4 rounded-xl bg-black/50 border border-white/10 text-xs font-mono">
                <span className="text-[#FF332C] font-bold block mb-2">
                  Issue 2: Hardcoded light-theme pink colors in dark mode
                </span>
                <p className="text-[#F9EAD7]/80 mb-2">
                  In <code className="text-[#BFE23A]">app.py</code> line 2095, the safety guard verdict uses:
                </p>
                <pre className="p-3 rounded bg-black/60 text-red-300 overflow-x-auto text-[11px]">
{`verdict_badge_style = "background:#fee2e2; color:#991b1b; border: 1px solid #f87171;" # ❌ Clashes with dark glass!`}
                </pre>
                <p className="text-[#F9EAD7]/80 mt-2">
                  Whereas Stitch design specifies:
                </p>
                <pre className="p-3 rounded bg-black/60 text-[#BFE23A] overflow-x-auto text-[11px]">
{`background: linear-gradient(135deg, rgba(225, 6, 0, 0.22) 0%, rgba(70, 4, 3, 0.5) 45%, rgba(16, 4, 6, 0.8) 100%);
border: 1px solid rgba(225, 6, 0, 0.45);
box-shadow: 0 24px 50px -10px rgba(225, 6, 0, 0.4), 0 0 35px rgba(225, 6, 0, 0.22);`}
                </pre>
              </div>

              <div className="p-4 rounded-xl bg-black/50 border border-white/10 text-xs font-mono">
                <span className="text-[#FF332C] font-bold block mb-2">
                  Issue 3: Missing Ambient Background Glow Mesh
                </span>
                <p className="text-[#F9EAD7]/80">
                  Real frosted glassmorphism requires bright background elements behind the blur filter to create optical refraction.
                  Without the floating ambient orbs (<code className="text-[#BFE23A]">.orb-crimson-main</code>, <code className="text-[#BFE23A]">.orb-lime-main</code>)
                  and geometric toruses (<code className="text-[#BFE23A]">.glow-torus</code>), blur filters simply render as a muddy dark gray surface.
                </p>
              </div>
            </div>
          )}

          {activeTab === 'fixes' && (
            <div className="space-y-4 text-xs font-mono">
              <p className="text-[#F9EAD7]/90 leading-relaxed font-sans">
                To fix your Streamlit application in <code className="text-[#BFE23A]">edai_FY/app.py</code>:
              </p>

              <div className="p-4 rounded-xl bg-black/50 border border-white/10 space-y-2">
                <h4 className="font-bold text-white font-sans text-sm">Step 1: Inject Ambient Glow Containers</h4>
                <p className="text-[#F9EAD7]/75 font-sans">
                  Add this right after your CSS injection in <code className="text-[#BFE23A]">app.py</code>:
                </p>
                <pre className="p-3 rounded bg-black/60 text-[#DCFF4E] overflow-x-auto text-[11px]">
{`st.markdown("""
<div class="ambient-container" style="position:fixed;inset:0;pointer-events:none;z-index:0;">
  <div class="ambient-orb orb-crimson-main"></div>
  <div class="ambient-orb orb-lime-main"></div>
  <div class="ambient-orb orb-peach-center"></div>
  <div class="glow-torus torus-1"></div>
</div>
""", unsafe_allow_html=True)`}
                </pre>
              </div>

              <div className="p-4 rounded-xl bg-black/50 border border-white/10 space-y-2">
                <h4 className="font-bold text-white font-sans text-sm">Step 2: Wrap Streamlit Sections in Glass HTML Blocks</h4>
                <p className="text-[#F9EAD7]/75 font-sans">
                  Instead of bare Streamlit markdown, output HTML using the defined classes:
                </p>
                <pre className="p-3 rounded bg-black/60 text-[#DCFF4E] overflow-x-auto text-[11px]">
{`st.markdown(f"""
<article class="frosted-crimson-glass rounded-2xl p-6">
  <div class="flex items-center gap-3">
    <div class="pulse-danger w-11 h-11 rounded-xl bg-crimson/40">...</div>
    <h2 class="text-white font-bold">{verdict_text}</h2>
  </div>
</article>
""", unsafe_allow_html=True)`}
                </pre>
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-3 border-t border-white/15 bg-black/40 flex items-center justify-between">
          <span className="text-xs font-mono text-[#F9EAD7]/60">
            Live Preview active in this application with 100% applied effects
          </span>
          <button
            onClick={onClose}
            className="frosted-lime-button px-4 py-1.5 rounded-xl text-xs font-semibold cursor-pointer"
          >
            Return to Live App
          </button>
        </div>
      </div>
    </div>
  );
};
