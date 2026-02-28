# HypaSense Labs Hackathon Pitch Script (5:00)

## Speaking Roles
- **Dom**: chemistry, contamination physics, hardware design
- **Niki**: digital twin, optimizer logic, UI walkthrough lead

## Run of Show (Timed Script + Exact UI Actions)

### 0:00-0:25 | Impactful Opening

**Dom:** [UI ACTION: Keep landing/title visible] Cooling towers quietly concentrate contaminants until one invisible chemistry shift becomes a compliance problem.  
**Dom:** If you only monitor at discharge, you learn too late and without root cause.  
**Niki:** HypaSense Labs gives operators earlier visibility: where contamination starts, what it will become at blowdown, and what to change now.

---

### 0:25-1:20 | Core Chemistry + Hardware Positioning

**Dom:** [UI ACTION: Move to architecture or process graphic] We monitor four nodes in sequence: **Makeup Water Intake**, **Basin (Post-Chemical)**, **Post-Heat Exchanger**, and **Discharge Line**.  
**Dom:** At every node, we measure **pH**, **conductivity**, and **turbidity**. Node deltas isolate source: concentration rise, corrosion signatures, and solids loading.  
**Niki:** The software then turns those readings into a live digital twin and optimized control recommendations.  
**Dom:** Hardware note for judges: the full sensing architecture is designed and mapped in our documentation. For this hackathon demo, we run **software-injected mock live data** because full hardware integration was not completed in time.

---

### 1:20-1:50 | Enter the App

**Niki:** [UI ACTION: Open `/auth`] We start at the sign-in screen branded **HypaSense Labs** with **Intelligent Water Management**.  
**Niki:** [UI ACTION: Enter credentials, click `Sign In`] Once signed in, we enter the digital twin of a cooling tower.

---

### 1:50-3:35 | Dashboard Walkthrough (Explain Every Component)

**Niki:** [UI ACTION: Show app header at `/app`] At the top header, you see the brand, two tabs, and system controls.  
**Niki:** Component 1: **Tab selector** with `Process Flow` and `Monitoring`.  
**Niki:** Component 2: **Backend status indicator** and status text cycling through `Idle`, `Loading`, `Connected`, or `Polling`.  
**Niki:** Component 3: **Collection control button**: `Start collecting data` -> `Starting...` -> `Collecting`.  
**Niki:** Component 4: active user name and sign-out icon.

**Dom:** [UI ACTION: Click `Start collecting data`] Once collecting starts, we stream updates every cycle into the twin and recommendation engine.

**Niki:** [UI ACTION: Point to `Demo Event Injection` card] This is the explicit demo-controls panel.  
**Niki:** It contains four manual event buttons: `Corrosion Spike`, `pH Drop`, `Turbidity Event`, and `Biocide Overdose`.  
**Niki:** These buttons are intentionally disabled until collection starts, then each shows `Injecting...` while the event is applied.

**Niki:** [UI ACTION: Click `Process Flow` tab] In `Process Flow`, we narrate the twin state by node and chemistry progression through the loop.  
**Dom:** This is where we explain contamination origin from node-to-node changes.

**Niki:** [UI ACTION: Click `Monitoring` tab and scroll through data area] In `Monitoring`, we focus on time-evolving behavior and control outcomes.  
**Niki:** Here is exactly what the monitored data model tracks:
- Per-node readings for all four nodes: pH, conductivity, turbidity  
- Twin metrics: CoC, estimated Cu, estimated Zn, biocide residual, compliance flag  
- Recommendation outputs: `Discharge Rate (m3/day)`, `Biocide Dose (mg/L)`, `pH Setpoint`, `CoC Target` with direction (`INCREASE/DECREASE/RAISE/LOWER`)  
- Reasoning text that explains why the recommendation changed  
- Historical trends for `cu`, `biocide`, `coc`, and `turbidity at node 4`

---

### 3:35-4:35 | Live Demo Sequence (Virtual Spikes)

**Dom:** [UI ACTION: Back to `Process Flow` for causality, then Monitoring for trends] We now run the demo events as a three-act story.  
**Dom:** Act 1: concentration/corrosion stress appears in upstream-to-midstream transitions.  
**Niki:** [UI ACTION: Click `Corrosion Spike`] We inject virtual corrosion and watch risk move in inferred metals and recommendations.  
**Dom:** [UI ACTION: Click `Turbidity Event`] Next we inject virtual turbidity and track solids impact through to discharge-side monitoring.  
**Niki:** [UI ACTION: Click `pH Drop`] Then we inject pH drop, which increases metal-solubility risk and forces a control response.  
**Niki:** [UI ACTION: Scroll down monitoring area] You can see trend movement plus recommendation deltas, not just static alarms.

---

### 4:35-4:50 | Market + Brief GTM (Back Section)

**Dom:** [UI ACTION: Move to back/market slide] Demand is real: the IEA indicates space-cooling demand could triple by 2050, and AI growth is pushing large water footprints.  
**Niki:** GTM in one line: start with data centers and industrial cooling sites that already face compliance pressure, then expand via pilot-to-annual SaaS + optimization support.

---

### 4:50-5:00 | Close

**Dom:** HypaSense Labs makes cooling chemistry visible before discharge failure.  
**Niki:** The digital twin converts that visibility into specific control actions in real time.  
**Both:** Detect earlier. Act faster. Pollute less.

## Presenter Notes
- Keep this flow strict: `Sign In` -> `/app` -> `Start collecting data` -> `Process Flow` -> inject events -> `Monitoring` -> scroll through live data -> back/market slide.
- If timing runs long, shorten the bulleted list under `Monitoring` by reading only the first three bullets.
- Market section is intentionally short (~10-15 seconds) per request.

## Source Notes
- Technical architecture and chemistry logic come from `BIOHACKFINALIDEA.pdf`.
- UI labels and tab/button names are taken from the current frontend pages and hooks (`Auth`, `LiveDashboard`, `useLiveDashboard`).
