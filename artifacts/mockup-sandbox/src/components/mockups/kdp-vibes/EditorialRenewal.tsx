import "./vibes.css";

export function EditorialRenewal() {
  return (
    <div className="vibe-frame vibe-editorial">
      <div className="vibe-intro">
        <span className="vibe-kicker">VIBE 02 · EDITORIAL RENEWAL</span>
        <h1>Make the milestone visible.</h1>
        <p>A confident, magazine-like system that treats recovery as a story of identity and momentum.</p>
      </div>
      <div className="vibe-spread">
        <section className="paper interior-paper">
          <div className="editorial-number">24</div>
          <div className="paper-topline">
            <span>RECOVERY / DAILY PRACTICE</span>
            <span>90 DAYS</span>
          </div>
          <h2>What will<br /><em>move me forward?</em></h2>
          <p className="paper-prompt">Use this page as a pause between the person you were and the person you are becoming.</p>
          <div className="editorial-grid">
            <div className="wide-field"><label>THE CHECK-IN</label><i /><i /><i /></div>
            <div><label>ENERGY</label><div className="scale">1 — 2 — 3 — 4 — 5</div></div>
            <div><label>SUPPORT I CAN REACH FOR</label><i /><i /></div>
            <div><label>ONE WIN, HOWEVER SMALL</label><i /><i /></div>
          </div>
          <div className="editorial-quote">“Progress is a practice.”</div>
        </section>
        <section className="paper cover-paper">
          <div className="editorial-cover-block" />
          <div className="cover-mark">BMP / 002</div>
          <div className="cover-copy">
            <span className="cover-eyebrow">A DAILY PRACTICE</span>
            <h2>Sobriety<br /><em>Recovery</em></h2>
            <div className="cover-divider" />
            <p>90 days of honest reflection, grounded choices, and forward motion.</p>
          </div>
          <div className="cover-footer">BRIGHT MINDFUL PAGES · JOURNAL SERIES</div>
        </section>
      </div>
      <div className="vibe-note">Layout: asymmetric editorial grid · bold typographic cover with one strong focal block</div>
    </div>
  );
}