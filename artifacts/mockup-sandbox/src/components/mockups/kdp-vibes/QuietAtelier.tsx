import "./quietatelier.css";

export function QuietAtelier() {
  return (
    <div className="atelier-frame">
      <header className="atelier-intro">
        <span className="atelier-kicker">VIBE 04 · QUIET ATELIER</span>
        <h1>A private ritual for becoming.</h1>
        <p>Warm, tactile pages that turn a daily recovery practice into a small act of self-respect.</p>
      </header>

      <div className="atelier-spread">
        <section className="atelier-paper atelier-interior">
          <div className="atelier-page-number">24</div>
          <div className="atelier-topline">
            <span>FIELD NOTES / RECOVERY</span>
            <span>90 DAYS</span>
          </div>
          <div className="atelier-rule" />
          <h2>The day is<br /><em>still yours.</em></h2>
          <p className="atelier-prompt">
            Before the noise arrives, make a little room for what is true.
          </p>

          <div className="atelier-checkin">
            <div className="atelier-field atelier-field-wide">
              <label>01 / HOW I AM ARRIVING</label>
              <i /><i /><i />
            </div>
            <div className="atelier-field">
              <label>02 / ENERGY</label>
              <div className="atelier-scale"><b>1</b><span /><b>2</b><span /><b>3</b><span /><b>4</b><span /><b>5</b></div>
            </div>
            <div className="atelier-field">
              <label>03 / WHAT I NEED</label>
              <i /><i />
            </div>
            <div className="atelier-field atelier-field-wide">
              <label>04 / ONE HONEST WIN</label>
              <i /><i />
            </div>
          </div>

          <div className="atelier-footer-quote">A little steadiness is still steadiness.</div>
        </section>

        <section className="atelier-paper atelier-cover">
          <div className="atelier-cover-sun" />
          <div className="atelier-cover-stamp">BMP<br /><span>FIELD EDITION</span></div>
          <div className="atelier-cover-copy">
            <span className="atelier-eyebrow">A DAILY FIELD GUIDE</span>
            <h2>Sobriety<br /><em>&amp; Recovery</em></h2>
            <div className="atelier-cover-rule" />
            <p>90 days of clear mornings, honest notes, and the next right thing.</p>
          </div>
          <div className="atelier-cover-side">VOL. 01&nbsp;&nbsp;&nbsp; / &nbsp;&nbsp;&nbsp;BMP</div>
          <div className="atelier-cover-footer">BRIGHT MINDFUL PAGES<br /><span>MAKE SPACE FOR THE LIFE AHEAD</span></div>
        </section>
      </div>

      <div className="atelier-note">Layout: tactile field-note interior · restrained gallery cover with a sun-washed paper mark</div>
    </div>
  );
}