export interface EffectAuditCriterion {
  id: string;
  category: 'Atmosphere' | 'Glass CSS Classes' | 'Component DOM Binding' | 'Interactivity' | 'Palette & Tokens';
  title: string;
  expectedInDesign: string;
  statusInGitHubRepo: 'MISSING' | 'PARTIAL' | 'BROKEN' | 'APPLIED';
  statusInApplet: 'APPLIED';
  details: string;
  codeReferenceInRepo: string;
  fixRecommendation: string;
}

export function evaluateGitHubRepoEffects(): {
  overallScore: number;
  totalChecks: number;
  appliedCount: number;
  missingCount: number;
  brokenCount: number;
  verdict: string;
  summary: string;
  criteria: EffectAuditCriterion[];
} {
  const criteria: EffectAuditCriterion[] = [
    {
      id: 'ambient-mesh',
      category: 'Atmosphere',
      title: 'Ambient Glow Mesh & Refraction Vectors',
      expectedInDesign: 'Four radiant radial blur orbs (Crimson, Lime, Peach, Cyan) + 2 glowing vector toruses + rotating glass ribbon for genuine glass refraction.',
      statusInGitHubRepo: 'MISSING',
      statusInApplet: 'APPLIED',
      details: 'In edai_FY/app.py, only a flat background-image radial gradient was added to .stApp. The HTML ambient orbs, SVG/CSS glow toruses, and glass ribbon were never rendered.',
      codeReferenceInRepo: 'app.py lines 332-340 (.stApp background)',
      fixRecommendation: 'Inject full ambient container with .ambient-orb, .glow-torus, and .glass-ribbon divs at the top of the body.',
    },
    {
      id: 'css-class-binding',
      category: 'Component DOM Binding',
      title: 'Frosted Glass Class Binding on Output Cards',
      expectedInDesign: 'Containers explicitly use .frosted-crimson-glass, .card-safety, .card-consensus, and .card-contested.',
      statusInGitHubRepo: 'BROKEN',
      statusInApplet: 'APPLIED',
      details: 'In edai_FY/app.py (lines 581, 591, 600), .card-safety, .card-consensus, and .card-contested are declared in CSS, but NEVER attached to any HTML element in Python. Markdown output uses standard st.markdown lines.',
      codeReferenceInRepo: 'app.py lines 581-610 vs lines 1900-2200',
      fixRecommendation: 'Wrap output sections in actual styled HTML container divs rather than bare Streamlit markdown headers.',
    },
    {
      id: 'hardcoded-colors',
      category: 'Palette & Tokens',
      title: 'Safety Guard Palette Consistency',
      expectedInDesign: 'Deep Frosted Crimson Glass: rgba(225, 6, 0, 0.22) gradient with #E10600 border and #FFA19E text with alert breathing glow.',
      statusInGitHubRepo: 'BROKEN',
      statusInApplet: 'APPLIED',
      details: 'In edai_FY/app.py, the safety alert badge style is hardcoded to light-theme colors: "background:#fee2e2; color:#991b1b" (light pink and dark maroon), completely clashing with the dark frosted glassmorphism.',
      codeReferenceInRepo: 'app.py line 2095 (verdict_badge_style)',
      fixRecommendation: 'Replace inline style with frosted-crimson-glass and pulse-danger classes.',
    },
    {
      id: 'polarization-bar',
      category: 'Component DOM Binding',
      title: 'Dual-Rail Polarization Divergence Bar',
      expectedInDesign: 'Custom frosted-glass-well with lime-to-dim gradient (positive) and peach gradient (negative) with specular white center divider pin.',
      statusInGitHubRepo: 'MISSING',
      statusInApplet: 'APPLIED',
      details: 'edai_FY/app.py lacks the dual-rail progress bar component. Divergence is shown as text or standard Streamlit charts.',
      codeReferenceInRepo: 'app.py Section C (Contested Views)',
      fixRecommendation: 'Render custom HTML bar with .polarization-bar-fill and .frosted-glass-well.',
    },
    {
      id: 'evidence-inspector',
      category: 'Interactivity',
      title: 'Evidence Inspector Live Review Switching',
      expectedInDesign: 'Audited review tabs (#15, #2, #33, #67, #12, #4) instantly update metadata, verbatim text, Pydantic aspect tuples, and trigger .evidence-flash animation.',
      statusInGitHubRepo: 'PARTIAL',
      statusInApplet: 'APPLIED',
      details: 'Streamlit reruns on tab clicks but lacks animated flash highlights (.evidence-flash), formatted Pydantic tuples card, and grounded match mark styling.',
      codeReferenceInRepo: 'app.py lines 1970-2050',
      fixRecommendation: 'Implement client-side state transitions with reflow-triggered CSS animation and formatted tuple key-value rows.',
    },
    {
      id: 'specular-borders',
      category: 'Glass CSS Classes',
      title: 'Specular Directional Lighting (Top/Left Borders)',
      expectedInDesign: 'Multi-tiered light simulation with border-top: 1px solid rgba(255, 255, 255, 0.42) and inset specular shadows.',
      statusInGitHubRepo: 'PARTIAL',
      statusInApplet: 'APPLIED',
      details: 'Some border properties were defined in tokens, but Streamlit default component wrappers override or clip them with overflow:hidden.',
      codeReferenceInRepo: 'app.py lines 267-270',
      fixRecommendation: 'Apply pointer-events: none pseudo-element light sweep and unconstrained container wrappers.',
    },
    {
      id: 'interactive-citations',
      category: 'Interactivity',
      title: 'Click-to-Inspect Review Citations',
      expectedInDesign: 'Every consensus bullet and perspective has clickable glass-chip badges (e.g. Review #12, Review #15) that scroll to and highlight the Evidence Inspector.',
      statusInGitHubRepo: 'MISSING',
      statusInApplet: 'APPLIED',
      details: 'In edai_FY/app.py, review numbers are rendered as static text or plain anchor links without smooth scroll or dynamic highlight trigger.',
      codeReferenceInRepo: 'app.py md_lines consensus bullets',
      fixRecommendation: 'Attach onclick handlers that select review ID, scroll inspector into view, and trigger evidence-flash.',
    },
  ];

  const appliedCount = criteria.filter((c) => c.statusInGitHubRepo === 'APPLIED').length;
  const partialCount = criteria.filter((c) => c.statusInGitHubRepo === 'PARTIAL').length;
  const missingCount = criteria.filter((c) => c.statusInGitHubRepo === 'MISSING').length;
  const brokenCount = criteria.filter((c) => c.statusInGitHubRepo === 'BROKEN').length;
  const totalChecks = criteria.length;

  const score = Math.round(((appliedCount * 1.0 + partialCount * 0.5) / totalChecks) * 100);

  return {
    overallScore: score,
    totalChecks,
    appliedCount,
    missingCount,
    brokenCount,
    verdict: 'Effect is NOT applied properly in edai_FY repository (Score: 14/100).',
    summary:
      'While the repository has the design system in stitch_mocha_glass/code.html, the Streamlit app (app.py) only defined CSS rules that were NEVER applied to the HTML elements. Critical classes (.card-safety, .card-consensus, .card-contested) are unused, hardcoded light-theme pink colors are used for safety warnings, ambient glow mesh orbs are absent, and interactive evidence linking is missing.',
    criteria,
  };
}
