import "./vibes.css";

export function CalmGarden() {
  return (
    <div className="vibe-frame vibe-calm">
      <div className="vibe-intro">
        <span className="vibe-kicker">VIBE 01 · CALM GARDEN</span>
        <h1>Small steps. Gentle progress.</h1>
        <p>Soft, reassuring pages for a recovery practice that feels private and steady.</p>
      </div>
      <div className="vibe-spread">
        <section className="paper interior-paper">
          <div className="paper-topline">
            <span>MY RECOVERY PLANNER</span>
            <span>DAY 24</span>
          </div>
          <div className="garden-rule" />
          <h2>Today, I choose<br /><em>one kind step.</em></h2>
          <p className="paper-prompt">A calm check-in for your body, mind, and support system.</p>
          <div className="mood-row">
            <span>How am I arriving?</span>
            <div className="mood-pills"><b>○</b><b>○</b><b>○</b><b>○</b><b>○</b></div>
          </div>
          <div className="writing-card">
            <strong>My intention for today</strong>
            <i /><i /><i />
          </div>
          <div className="two-cards">
            <div><strong>One thing I need</strong><i /><i /></div>
            <div><strong>One thing I can release</strong><i /><i /></div>
          </div>
          <div className="affirmation">I can begin again without starting over.</div>
        </section>
        <section className="paper cover-paper">
          <div className="cover-botanical botanical-a">✦</div>
          <div className="cover-botanical botanical-b">⌁</div>
          <div className="cover-mark">BMP</div>
          <div className="cover-copy">
            <span className="cover-eyebrow">BRIGHT MINDFUL PAGES</span>
            <h2>Sobriety<br /><em>&amp; Recovery</em></h2>
            <div className="cover-divider" />
            <p>A 90-Day<br />Undated Recovery Journal</p>
          </div>
          <div className="cover-footer">A quiet place to notice your progress</div>
        </section>
      </div>
      <div className="vibe-note">Layout: spacious single-column reflection page · premium matte journal cover</div>
    </div>
  );
}