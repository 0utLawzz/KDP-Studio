import "./vibes.css";

export function BrightMomentum() {
  return (
    <div className="vibe-frame vibe-momentum">
      <div className="vibe-intro">
        <span className="vibe-kicker">VIBE 03 · BRIGHT MOMENTUM</span>
        <h1>Celebrate every clear day.</h1>
        <p>High-energy, friendly pages that make the daily ritual feel achievable and rewarding.</p>
      </div>
      <div className="vibe-spread">
        <section className="paper interior-paper">
          <div className="momentum-banner">
            <span>DAY 24</span>
            <strong>YOU SHOWED UP.</strong>
            <span>KEEP GOING →</span>
          </div>
          <div className="paper-topline">
            <span>MY RECOVERY CHECK-IN</span>
            <span>90-DAY TRACKER</span>
          </div>
          <h2>Today&apos;s<br /><em>bright spots</em></h2>
          <div className="bright-fields">
            <div><span>☀</span><label>Something I&apos;m proud of</label><i /><i /></div>
            <div><span>♡</span><label>Someone who helped me</label><i /><i /></div>
            <div><span>→</span><label>My next right step</label><i /><i /></div>
          </div>
          <div className="check-strip">
            <strong>Today I practiced</strong>
            <span>□ honesty</span><span>□ patience</span><span>□ asking for help</span>
          </div>
          <div className="momentum-footer">Tiny choices add up to a changed life.</div>
        </section>
        <section className="paper cover-paper">
          <div className="sunburst" />
          <div className="cover-mark">BMP</div>
          <div className="cover-copy">
            <span className="cover-eyebrow">BRIGHT MINDFUL PAGES</span>
            <h2>Sobriety<br /><em>&amp; Recovery</em></h2>
            <div className="cover-divider" />
            <p>90-Day Daily Tracker</p>
          </div>
          <div className="cover-sticker">ONE DAY<br />AT A TIME</div>
          <div className="cover-footer">A practical journal for steady, hopeful progress</div>
        </section>
      </div>
      <div className="vibe-note">Layout: modular prompt cards · bright badge-led cover built for thumbnail impact</div>
    </div>
  );
}